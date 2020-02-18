from django.contrib.auth.models import AnonymousUser
from django.http import parse_cookie
from django.conf import settings
from django.contrib.auth import load_backend, BACKEND_SESSION_KEY, SESSION_KEY
import importlib

from asgiref.sync import sync_to_async


async def get_user(scope):
    if "headers" not in scope:
        raise ValueError(
            "Headers weren't found in the websocket scope."
        )
    for name, value in scope.get("headers", []):
        if name == b"cookie":
            try:
                session_id = parse_cookie(value.decode("ascii"))["sessionid"]
                break
            except KeyError:
                # Attempt to find JWT for authentication with simple JWT
                return AnonymousUser()

    engine = importlib.import_module(settings.SESSION_ENGINE)
    if not sync_to_async(engine.SessionStore().exists(session_id)):
        print("Session Key does not exist. Expired?")
        return AnonymousUser()

    session = sync_to_async(engine.SessionStore(session_id))
    data = session.load()

    print('Session to Expire: %s' % session.get_expiry_date())
    print('Raw Data: %s' % data)
    uid = data.get(SESSION_KEY, None)
    backend_path = data.get(BACKEND_SESSION_KEY, None)

    if backend_path is None:
        print('No authentication backend associated with session')
        return

    if uid is None:
        print('No user associated with session')
        return

    backend = load_backend(backend_path)
    user = backend.get_user(user_id=uid)
    if user is None:
        print("No user associated with that id.")
        return

    return user
