from django import forms
from .models import FormTemplate, FormField, FIELD_TYPES
from django.forms import Textarea

class FormTemplateForm(forms.ModelForm):
    class Meta:
        model = FormTemplate
        fields = ['name', 'description', 'is_public']


class FormFieldForm(forms.ModelForm):
    class Meta:
        model = FormField
        fields = ['label', 'field_type', 'required']


# توليد نموذج ديناميكي لملء الفورم
def generate_dynamic_form(form_template):
    class DynamicForm(forms.Form):
        pass

    for field in form_template.fields.all():
        kwargs = {'label': field.label, 'required': field.required}

        if field.field_type == 'text':
            form_field = forms.CharField(**kwargs)
        elif field.field_type == 'textarea':
            kwargs['widget'] = Textarea
            form_field = forms.CharField(**kwargs)
        elif field.field_type == 'email':
            form_field = forms.EmailField(**kwargs)
        elif field.field_type == 'number':
            form_field = forms.IntegerField(**kwargs)
        elif field.field_type == 'file':
            form_field = forms.FileField(**kwargs)
        elif field.field_type == 'date':
            form_field = forms.DateField(**kwargs)
        elif field.field_type == 'checkbox':
             kwargs['label'] = field.label
             kwargs['required'] = False  # checkboxes غالباً لا تكون مطلوبة
             kwargs['widget'] = forms.CheckboxInput()
             form_field = forms.BooleanField(**kwargs)
        else:
            continue

        DynamicForm.base_fields[f'field_{field.id}'] = form_field

    return DynamicForm
