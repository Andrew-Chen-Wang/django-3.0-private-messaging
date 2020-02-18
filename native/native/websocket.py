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
