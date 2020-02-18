from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User


class UserCreationFormWithoutUsername(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserCreationForm):
        model = User
        fields = ("email",)
