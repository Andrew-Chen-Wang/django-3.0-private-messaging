from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.core.mail import send_mail

from .managers import CustomUserManager

# TODO IF need to change backend since no username: https://stackoverflow.com/questions/37332190/django-login-with-email


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=150)

    in_chat = models.ForeignKey(
        "MessageThread",
        on_delete=models.SET_NULL,
        null=True, default=None
    )

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.get_full_name()

    class Meta:
        swappable = "AUTH_USER_MODEL"

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


"""
REMEMBER, I am NOT designing a group chat, only private messaging
and that private messaging only activates
"""


# Each message thread can only have two users for MY case
# DO NOT QUERY this model to see which message thread a user is in.
class MessageThread(models.Model):
    id = models.BigAutoField(primary_key=True)
    user1 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="user1")
    user2 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="user2")


"""
For legal reasons, we (as in me) will not allow users to delete their messages
in case an audit must occur. Any chat app that follows Section 230
should be wise when it comes to this; even with black market deals
being legal for you to not worry about, it ruins your reputation
"""


class Message(models.Model):
    id = models.UUIDField(primary_key=True)
    # Since an insertion in the database in context of UUID field
    # is basically appending to the end of the database
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    message = models.TextField(max_length=918)
    thread = models.ForeignKey(MessageThread, on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    # You can add a updated field if you wish with auto_now for updating messages. I will not.
