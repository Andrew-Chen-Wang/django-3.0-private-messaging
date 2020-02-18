"""
This is where we handle all our socket connections.
All the functions use see here are supposed to reduce
the space and split the logic between each type of
websocket event.
"""


async def connect(event, scope, receive, send):
    # Handle logic, e.g. auth, once user connects
    await send({
        'type': 'websocket.accept'
    })


async def disconnect(event, scope, receive, send):
    # WebSocket connection breaks right after.
    # Handle anything before the connection disconnects.
    pass


async def receive(event, scope, receive, send):
    # Handle logic when server receives something, like a message.
    if event['text'] == 'ping':
        await send({
            'type': 'websocket.send',
            'text': 'pong!'
        })
    print(event)
