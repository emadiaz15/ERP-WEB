from channels.generic.websocket import AsyncWebsocketConsumer
# apps/notifications/consumers.py
import logging
from typing import Any, Dict

log = logging.getLogger("ws.consumer")

class NotificationsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        uid = getattr(user, "id", None)
        err = getattr(self.scope, "jwt_error", None)
        if not uid:
            log.warning(f"[WS][notifications][reject] reason={err or 'missing-token'}")
            await self.close(code=4001)
            return
        self.group_name = f"user_{uid}"
        try:
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()  # <- **esto faltaba**
            # Nivel reducido por defecto (WARNING en logger) salvo WS_VERBOSE_LOG=True
            log.debug(f"[WS][notifications][accept] user={uid} group={self.group_name}")
        except Exception as e:
            log.warning(f"[WS][notifications][error] on connect: {e}")
            await self.close(code=1011)

    async def disconnect(self, code):
        import time
        start = time.time()
        try:
            had_group = hasattr(self, "group_name") and getattr(self, "group_name", None)
            log.debug(f"[WS][notifications][disconnect] start group_discard group={getattr(self, 'group_name', None)} channel={self.channel_name}")
            if had_group:
                await self.channel_layer.group_discard(self.group_name, self.channel_name)
        except Exception as e:
            log.warning(f"[WS][notifications][disconnect][warn] {e}")
        finally:
            elapsed = time.time() - start
            log.debug(f"[WS][notifications][disconnect] code={code} elapsed={elapsed:.3f}s")

    # Consumer de prueba de salud
class PingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Acepta conexión de ping para verificación de salud."""
        await self.accept()
        log.debug("[WS][ping][accept]")

    async def disconnect(self, code):
        log.debug(f"[WS][ping][disconnect] code={code}")
    async def receive(self, text_data=None, bytes_data=None):
        # Optional: respond to ping
        import json
        try:
            data = json.loads(text_data or "{}")
            if data.get("type") == "ping":
                await self.send(text_data=json.dumps({"type": "pong"}))
        except Exception:
            pass

    async def notify_message(self, event: Dict[str, Any]):
        payload = event.get("data", event)
        import json
        await self.send(text_data=json.dumps(payload))
