from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import Userloginform
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout


def login(request):
    # Agar user login bo'lgan bo'lsa, indexga yuboramiz
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = Userloginform(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Foydalanuvchini tekshiramiz
            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)
                return redirect('index')
            else:
                messages.error(request, "Login yoki parol noto'g'ri!")
    else:
        form = Userloginform(request)

    return render(request, 'users/login.html', {'form': form})


def logout(request):
    auth_logout(request)
    return redirect('login')
