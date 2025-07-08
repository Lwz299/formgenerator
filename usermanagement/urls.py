from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),

    # reset password (view مخصصة ترسل الإيميل)
    path('reset_password/', views.reset_password, name='reset_password'),

    # هذه المسارات مطلوبة من Django لإنشاء روابط البريد
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),

    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_sent.html'
    ), name='password_reset_done'),

    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
]
