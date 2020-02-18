from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name="index"),

    # Authentication
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/register/", views.register, name="register"),

    # Test URLs
    path("test/wsconn", views.wsconn, name="wsconntest"),

    # Chat URL
    path("chat/<int:thread>", views.open_chat, name="chat")
]
