from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.http import Http404, HttpResponseForbidden, JsonResponse

from .forms import UserCreationFormWithoutUsername
from .models import User, MessageThread


def index(request):
    user = request.user
    if user.is_authenticated:
        # If a chat is terminated, make this None
        if user.in_chat is not None:
            return redirect("/chat/" + str(user.in_chat.id))
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
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return redirect("login/")

    # Identify the thread, if any, to go to.
    if thread is None:
        if request.user.in_chat is None:
            # No chat yet.
            return JsonResponse({"not found": "Create a chat in the admin for this user!"})
        else:
            thread = request.user.in_chat.id

    # Open the thread that user wants to view
    try:
        thread = MessageThread.objects.get(id=thread)
    except MessageThread.DoesNotExist:
        raise Http404("Message thread does not exist")
    if request.user not in (thread.user1, thread.user2):
        return HttpResponseForbidden("You are not a part of this chat")
    # Check if this chat can send messages.
    target_user = thread.user1 if thread.user1 != request.user else thread.user2
    if not target_user.is_active:
        target_user = target_user.id
    else:
        target_user.get_full_name()
    context = {
        "target_user": target_user,
    }
    if thread != request.user.in_chat:
        # User can't talk in chat
        context["sendable"] = False
        return render(request, "chat/chat.html", context=context)
    else:
        context["sendable"] = True
        return render(request, "chat/chat.html", context=context)
