import base64
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import FormTemplate, FormField, FormSubmission, FieldValue
from .forms import FormTemplateForm, FormFieldForm, generate_dynamic_form
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

@login_required
def create_form_template(request):
    if request.method == 'POST':
        form = FormTemplateForm(request.POST)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.created_by = request.user
            new_form.save()
            return redirect('add_fields', form_id=new_form.id)
    else:
        form = FormTemplateForm()
    return render(request, 'create_form.html', {'form': form})

@login_required
def add_fields(request, form_id):
    form_template = get_object_or_404(FormTemplate, id=form_id)
    if request.method == 'POST':
        field_form = FormFieldForm(request.POST)
        if field_form.is_valid():
            new_field = field_form.save(commit=False)
            new_field.form = form_template
            new_field.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': field_form.errors}, status=400)

    field_form = FormFieldForm()
    fields = form_template.fields.all()
    return render(request, 'add_fields.html', {
        'field_form': field_form,
        'fields': fields,
        'form_template': form_template
    })

@login_required
def ajax_delete_field(request, field_id):
    if request.method == 'POST':
        field = get_object_or_404(FormField, id=field_id)
        field.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@login_required
def ajax_get_field(request, field_id):
    if request.method == 'GET':
        field = get_object_or_404(FormField, id=field_id)
        data = {
            'id': field.id,
            'label': field.label,
            'field_type': field.field_type,
            'required': field.required
        }
        return JsonResponse(data)
    return JsonResponse({'success': False}, status=400)

@csrf_exempt
@login_required
def ajax_update_field(request, field_id):
    if request.method == 'POST':
        field = get_object_or_404(FormField, id=field_id)
        field.label = request.POST.get('label')
        field.field_type = request.POST.get('field_type')
        field.required = request.POST.get('required') == 'true'
        field.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

def preview_form(request, form_id):
    form_template = get_object_or_404(FormTemplate, id=form_id)
    fields = FormField.objects.filter(form=form_template)
    return render(request, 'preview_form.html', {
        'form_template': form_template,
        'fields': fields
    })

def fill_form(request, form_id):
    form_template = get_object_or_404(FormTemplate, id=form_id)

    if not form_template.is_public and not request.user.is_authenticated:
        return redirect('login')

    DynamicForm = generate_dynamic_form(form_template)

    if request.method == 'POST':
        form = DynamicForm(request.POST, request.FILES)
        if form.is_valid():
            submission = FormSubmission.objects.create(
                form=form_template,
                user=request.user if request.user.is_authenticated else None
            )
            for field in form_template.fields.all():
                field_key = f'field_{field.id}'

                value = form.cleaned_data.get(field_key)
                if field.field_type == 'file':
                    file_content =value.read()
                    base64_data = base64.b64encode(file_content).decode('utf-8')
                    mime_type = value.content_type
                    full_value = f"{mime_type};base64,{base64_data}"
                    FieldValue.objects.create(submission=submission, field=field, value=full_value)
                else:
                    FieldValue.objects.create(submission=submission, field=field, value=value)



                field_value = FieldValue(submission=submission, field=field)

                if field.field_type == 'file':
                    field_value.uploaded_file = value
                else:
                    field_value.value = value

                field_value.save()

            return render(request, 'thank_you.html')
    else:
        form = DynamicForm()

    return render(request, 'fill_form.html', {'form': form, 'form_template': form_template})

def home(request):
    forms = FormTemplate.objects.filter(is_public=True)
    return render(request, 'home.html', {'forms': forms})

def view_submissions(request, form_id):
    form_template = get_object_or_404(FormTemplate, id=form_id)

    # تأكد أن المستخدم هو من أنشأ النموذج
    if form_template.created_by != request.user:
        raise Http404("غير مصرح لك بعرض هذه الصفحة.")

    # استخدام related_name الصحيح: 'values__field'
    submissions = FormSubmission.objects.filter(form=form_template).prefetch_related('values__field')

    return render(request, 'view_submissions.html', {
        'form_template': form_template,
        'submissions': submissions,
    })


@login_required
def delete_form_template(request, form_id):
    form_template = get_object_or_404(FormTemplate, id=form_id)

    # تحقق أن المستخدم هو مالك النموذج
    if form_template.created_by != request.user:
        messages.error(request, "ليس لديك صلاحية لحذف هذا النموذج.")
        return redirect('home')  # أو صفحة أخرى مناسبة

    if request.method == 'POST':
        form_template.delete()
        messages.success(request, "تم حذف النموذج بنجاح.")
        return redirect('home')  # أو صفحة إدارة النماذج

    # لو كانت الطريقة GET يمكن عرض صفحة تأكيد الحذف (اختياري)
    return render(request, 'confirm_delete.html', {
        'form_template': form_template,
    })

def download_base64_file(request, value_id):
    try:
        field_value = FieldValue.objects.get(id=value_id)
        base64_str = field_value.value

        if not base64_str or ';base64,' not in base64_str:
            raise Http404("ملف غير موجود أو غير صالح")

        mime_type, b64data = base64_str.split(';base64,', 1)
        file_data = base64.b64decode(b64data)

        response = HttpResponse(file_data, content_type=mime_type)
        response['Content-Disposition'] = f'inline; filename="file_{field_value.id}"'
        return response

    except FieldValue.DoesNotExist:
        raise Http404("لم يتم العثور على الملف")
    except Exception:
        raise Http404("حدث خطأ أثناء تحميل الملف")