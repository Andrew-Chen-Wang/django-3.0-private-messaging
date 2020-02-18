from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.http import Http404, HttpResponseForbidden

from .forms import UserCreationFormWithoutUsername
from .models import User, MessageThread


def index(request):
    user = request.user
    if user.is_authenticated:
        if user.in_chat is not None:
            redirect("/chat/" + user.in_chat.id)
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


# Chat Application
# In order for there to be any chat, you need to first render the template
def open_chat(request, thread: int):
    if thread is None:
        if request.user.in_chat is None:
            # No chat yet.
            pass
        else:
            return render(request, "chat/chat.html", context={"sendable": True})
    else:
        # Open the thread that user wants to view
        try:
            thread = MessageThread.objects.get(id=thread)
        except MessageThread.DoesNotExist:
            raise Http404("Message thread does not exist")
        if not (thread.user1 or thread.user2) == request.user:
            return HttpResponseForbidden("You are not a part of this chat")
        # Check if this chat can send messages.
        if thread != request.user.in_chat:
            # User can't talk in chat
            return render(request, "chat/chat.html", context={"sendable": False})
        else:
            return render(request, "chat/chat.html", context={"sendable": True})
