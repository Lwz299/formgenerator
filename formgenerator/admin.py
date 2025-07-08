from django.contrib import admin
from .models import FormTemplate, FormField, FormSubmission, FieldValue
# Register your models here.


admin.site.register(FormTemplate)
admin.site.register(FormField)
admin.site.register(FormSubmission)
admin.site.register(FieldValue) 