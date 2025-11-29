import logging
from urllib.parse import parse_qs

from django.contrib.auth.models import AnonymousUser
from asgiref.sync import sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication

log = logging.getLogger("ws.jwt")

class JWTAuthMiddleware:
    """
    Middleware ASGI para Channels que autentica por:
      - querystring: ?token=<JWT>
      - o header:    Authorization: Bearer <JWT>
    y setea scope['user'].
    """
    def __init__(self, inner):
        self.inner = inner
        self.jwt_auth = JWTAuthentication()

    async def __call__(self, scope, receive, send):
        # 1) Leer token desde querystring (?token=...)
        raw_qs = scope.get("query_string", b"").decode()
        params = parse_qs(raw_qs or "")
        token = None
        if "token" in params and params["token"]:
            token = params["token"][0]
            # Evitar loguear tokens en producción
            log.debug("[WS][JWT] token recibido por querystring (oculto)")

        # 2) Fallback: Authorization: Bearer <JWT>
        if not token:
            try:
                for name, value in scope.get("headers", []):
                    if name == b"authorization":
                        v = value.decode()
                        if v.lower().startswith("bearer "):
                            token = v.split(" ", 1)[1].strip()
                            log.debug("[WS][JWT] token recibido por header (oculto)")
                        break
            except Exception:
                pass

        # 3) Validar y setear user
        user = AnonymousUser()
        if token:
            try:
                validated = self.jwt_auth.get_validated_token(token)
                user = await sync_to_async(self.jwt_auth.get_user)(validated)
                log.info(f"[WS][JWT] token válido (user_id={getattr(user, 'id', None)})")
            except Exception as e:
                log.warning(f"[WS][JWT] token inválido")
                user = AnonymousUser()
        else:
            log.debug("[WS][JWT] sin token recibido")

        scope["user"] = user
        return await self.inner(scope, receive, send)

def JWTAuthMiddlewareStack(inner):
    """Factory para usarlo directo en asgi.py"""
    return JWTAuthMiddleware(inner)
