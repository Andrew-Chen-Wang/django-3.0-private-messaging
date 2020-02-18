from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Message, MessageThread, User
from .forms import UserCreationFormWithoutUsername, CustomUserChangeForm

admin.site.register(MessageThread)


class MessageAdmin(admin.ModelAdmin):
    readonly_fields = ("created",)


admin.site.register(Message, MessageAdmin)


# https://testdriven.io/blog/django-custom-user-model/
class CustomUserAdmin(UserAdmin):
    add_form = UserCreationFormWithoutUsername
    form = CustomUserChangeForm
    list_display = ("first_name", "last_name", 'email', 'is_staff', 'is_active',)
    list_filter = ("first_name", "last_name", 'email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ("first_name", "last_name", 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ("first_name", "last_name", 'email', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ("first_name", "last_name", 'email',)
    ordering = ("email",)


admin.site.register(User, CustomUserAdmin)
