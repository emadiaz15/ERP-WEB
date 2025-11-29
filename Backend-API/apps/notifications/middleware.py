from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from channels.middleware import BaseMiddleware
from asgiref.sync import sync_to_async
from django.apps import apps as django_apps
from django.conf import settings

@sync_to_async
def _get_user_by_id(user_id):
    try:
        User = django_apps.get_model(settings.AUTH_USER_MODEL)  # lazy
        return User.objects.get(id=user_id)
    except Exception:
        return AnonymousUser()

async def _get_user_from_token(token_str):
    try:
        token = AccessToken(token_str)
        user_id = token.get("user_id")
        if not user_id:
            return AnonymousUser()
        return await _get_user_by_id(user_id)
    except Exception:
        return AnonymousUser()

class JWTAuthMiddlewareQueryString(BaseMiddleware):
    """
    Lee ?token=<JWT> de la URL del WebSocket y setea scope['user'].
    Si no hay o es inválido -> AnonymousUser (el consumer puede cerrar).
    """
    async def __call__(self, scope, receive, send):
        scope["user"] = AnonymousUser()
        try:
            query = scope.get("query_string", b"").decode()
            token = parse_qs(query).get("token", [None])[0]
        except Exception:
            token = None

        if token:
            scope["user"] = await _get_user_from_token(token)

        return await super().__call__(scope, receive, send)
