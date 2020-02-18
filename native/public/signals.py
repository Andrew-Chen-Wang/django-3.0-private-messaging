"""
This is to keep track of the in_chat attribute in the
custom user model. Whenever a chat is created and a user
is added to it, we immediately need to change that user's
in_chat attribute to this new chat.
"""
from django.db.models.signals import post_save
from .models import MessageThread


def change_current_message(sender, instance, created, **kwargs):
    if created:
        # First we need to archive the old chats of users
        chat1 = instance.user1.in_chat
        if chat1 is not None:
            companion1 = instance.user1 if instance.user1 != chat1.user1 else chat1.user2
            companion1.in_chat = None
            companion1.save()

        # Repeat for second user
        chat2 = instance.user2.in_chat
        if chat2 is not None:
            companion2 = instance.user2 if instance.user2 != chat2.user1 else chat2.user2
            companion2.in_chat = None
            companion2.save()

        instance.user1.in_chat = instance
        instance.user2.in_chat = instance
        instance.user1.save()
        instance.user2.save()


post_save.connect(change_current_message, sender=MessageThread)
