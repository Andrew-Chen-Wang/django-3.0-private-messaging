"""
ASGI config for native project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
# from .websocket import websocket_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'native.settings')

# https://dev.to/jaydenwindle/adding-websockets-to-your-django-app-with-no-extra-dependencies-2f6h
django_application = get_asgi_application()

from public.socket import handle_connect, handle_disconnect, handle_receive


async def websocket_application(scope, receive, send):
    while True:
        event = await receive()
        # This is the implementation of our business logic
        # Each function is located in socket.py to be more clean

        if event['type'] == 'websocket.connect':
            await handle_connect(event, scope, receive, send)

        if event['type'] == 'websocket.disconnect':
            await handle_disconnect(event, scope, receive, send)
            break

        if event['type'] == 'websocket.receive':
            await handle_receive(event, scope, receive, send)

async def application(scope, receive, send):
    if scope['type'] == 'http':
        await django_application(scope, receive, send)
    elif scope['type'] == 'websocket':
        await websocket_application(scope, receive, send)
    else:
        raise NotImplementedError(f"Unknown scope type {scope['type']}")
