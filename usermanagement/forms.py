from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from django.contrib.auth.forms import PasswordResetForm as DjangoPasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model


User = get_user_model()
class CustomUserCreationForm(UserCreationForm):
    """
    Custom form for user registration that extends the default UserCreationForm.
    """
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2')
class PasswordResetForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254, widget=forms.EmailInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Enter your email'}))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("No user is associated with this email address.")
        return email

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None):
        """
        Generates a one-use only link for resetting password and sends to the user.
        """
        email = self.cleaned_data["email"]
        for user in User.objects.filter(email=email):
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = token_generator.make_token(user)
            if not domain_override:
                domain = request.get_host()
            else:
                domain = domain_override
            protocol = 'https' if use_https else 'http'
            context = {
                'email': email,
                'domain': domain,
                'site_name': 'Your Site',
                'uid': uid,
                'user': user,
                'token': token,
                'protocol': protocol,
            }
            subject = render_to_string(subject_template_name, context)
            # Remove newlines to prevent header injection
            subject = ''.join(subject.splitlines())
            body = render_to_string(email_template_name, context)

            send_mail(subject, body, from_email or settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False, html_message=None)