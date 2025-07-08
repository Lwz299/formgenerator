# formgenerator/models.py

from django.db import models
from usermanagement.models import User

# Available field types for form fields
FIELD_TYPES = [
    ('text', 'Short Text'),
    ('textarea', 'Long Text'),
    ('email', 'Email'),
    ('number', 'Number'),
    ('file', 'File'),
    ('date', 'Date'),
    ('checkbox', 'Checkbox'),
]

# Main form template
class FormTemplate(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

# Fields associated with each form
class FormField(models.Model):
    form = models.ForeignKey(FormTemplate, on_delete=models.CASCADE, related_name='fields')
    label = models.CharField(max_length=255)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    required = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.form.name} - {self.label}"

# A form submission by a user
class FormSubmission(models.Model):
    form = models.ForeignKey(FormTemplate, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission #{self.id} - {self.form.name}"

# Submitted values for each field
class FieldValue(models.Model):
    submission = models.ForeignKey(FormSubmission, on_delete=models.CASCADE, related_name='values')
    field = models.ForeignKey(FormField, on_delete=models.CASCADE)
    value = models.TextField(blank=True, null=True)
    #uploaded_file = models.FileField(upload_to='uploads/', null=True, blank=True)

    def __str__(self):
        return f"{self.field.label}: {self.value or (self.uploaded_file.name if self.uploaded_file else '')}"
