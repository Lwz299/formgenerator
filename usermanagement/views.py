from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm,PasswordResetForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm
from django.conf import settings

from .models import User 
# Create your views here.
def login_view(request):
    if request.method =="POST":
        form =AuthenticationForm(request,data=request.POST)
        if form.is_valid():
            user= form.get_user()
            login(request,user)
            messages.success(request,"Login successful")
            return redirect('profile')
        else:
            messages.error(request,"Invalid username or password")
    else:
        form =AuthenticationForm()
    return render(request,'login.html',{'form':form})
############################################
def profile(request):
    if request.user.is_authenticated:
        return render(request,'profile.html',{'user':request.user})
    else:
        messages.error(request,"You need to login first")
        return redirect('login')
##########################################
def logout_view(request):
    logout(request)
    messages.success(request,"Logout successful")
    return redirect('login')
######################################
def home(request):
    return render(request,'home.html')
##########################################
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            messages.success(request,"Registration successful")
            return redirect('profile')
        else:
            messages.error(request,"Registration failed. Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})
##########################################
def reset_password(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                request=request,
                from_email=settings.DEFAULT_FROM_EMAIL,
                use_https=request.is_secure(),
            )
            messages.success(request, "Password reset link sent to your email.")
            return redirect('login')
        else:
            messages.error(request, "Invalid input. Please correct the errors below.")
    else:
        form = PasswordResetForm()
    return render(request, 'reset_password.html', {'form': form})