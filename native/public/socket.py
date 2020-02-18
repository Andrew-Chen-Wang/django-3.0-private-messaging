"""
This is where we handle all our socket connections.
All the functions use see here are supposed to reduce
the space and split the logic between each type of
websocket event.
"""
from .utils import get_user
from .models import MessageThread, Message


async def handle_connect(event, scope, receive, send):
    # Handle logic, e.g. auth, once user connects
    await send({
        'type': 'websocket.accept'
    })


async def handle_disconnect(event, scope, receive, send):
    # WebSocket connection breaks right after.
    # Handle anything before the connection disconnects.
    pass


async def handle_receive(event, scope, receive, send):
    # Handle logic when server receives something, like a message.
    """
    When a user connects, we need to identify which chat they're in.
    Then, send the message to that chat.
    """
    user = get_user(scope)
    # In case user tries to do something...
    if user.in_chat is None:
        return
    # Therefore, even if someone does try to infiltrate a chat...
    # They'll be sending any troll message to their current chat...
    thread = user.in_chat

    await send({
        "type": "websocket.send",
        "text": event["text"]
    })
    Message.objects.create(message=event["text"], thread=thread)
