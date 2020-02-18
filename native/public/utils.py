from django.conf import settings
from django.contrib.auth import (
    BACKEND_SESSION_KEY,
    HASH_SESSION_KEY,
    SESSION_KEY,
    get_user_model,
    load_backend,
)
from django.contrib.auth.models import AnonymousUser
from django.utils.crypto import constant_time_compare


def get_user(scope):
    # Taken straight from channels source code: https://github.com/django/channels/blob/master/channels/auth.py
    if "session" not in scope:
        raise ValueError(
            "Cannot find session in scope. You should wrap your consumer in SessionMiddleware."
        )
    session = scope["session"]
    user = None
    try:
        user_id = _get_user_session_key(session)
        backend_path = session[BACKEND_SESSION_KEY]
    except KeyError:
        pass
    else:
        if backend_path in settings.AUTHENTICATION_BACKENDS:
            backend = load_backend(backend_path)
            user = backend.get_user(user_id)
            # Verify the session
            if hasattr(user, "get_session_auth_hash"):
                session_hash = session.get(HASH_SESSION_KEY)
                session_hash_verified = session_hash and constant_time_compare(
                    session_hash, user.get_session_auth_hash()
                )
                if not session_hash_verified:
                    session.flush()
                    user = None
    return user or AnonymousUser()


def _get_user_session_key(session):
    # This value in the session is always serialized to a string, so we need
    # to convert it back to Python whenever we access it.
    return get_user_model()._meta.pk.to_python(session[SESSION_KEY])
