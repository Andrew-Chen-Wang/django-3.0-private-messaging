from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import authenticate, login

from .forms import UserCreationFormWithoutUsername
from .models import User


def index(request):
    user = request.user
    if user.is_authenticated:
        if user.in_chat is not None:
            redirect("/chat")
    return render(request, "index.html")


# Using my pre-made base template here:
# https://github.com/Andrew-Chen-Wang/base-django-project
# I've tweaked it so that there is only email and name
def register(request):
    """Using Django's pre-made UserCreationForm"""
    if request.method == "POST":
        form = UserCreationFormWithoutUsername(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password1")
            user = authenticate(username=email, password=password)
            login(request, user)
            return redirect("/")
        else:
            form = UserCreationFormWithoutUsername()
            return render(request, "registration/register.html", {"form": form})
    else:
        form = UserCreationFormWithoutUsername()
        return render(request, "registration/register.html", {"form": form})


# Testing plain JS WebSocket connection
def wsconn(request):
    # THIS IS NOT THE ASYNC CODE.
    # For the async code, go to socket.py
    return render(request, "misc/testingwsconn.html")

