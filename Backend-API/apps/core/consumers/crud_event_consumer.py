import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

log = logging.getLogger("ws.crud")

class CrudEventConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or getattr(user, "is_anonymous", True):
            log.info(f"[WS][crud][reject] anonymous user")
            await self.close(code=4401)
            return
        self.group_name = "crud_events"
        try:
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            log.info(f"[WS][crud][accept] user={getattr(user,'id',None)} group={self.group_name}")
        except Exception as e:
            log.warning(f"[WS][crud][error] on connect: {e}")
            await self.close(code=1011)

    async def disconnect(self, close_code):
        import time
        start = time.time()
        try:
            had_group = hasattr(self, "group_name") and getattr(self, "group_name", None)
            log.info(
                f"[WS][crud][disconnect] start group_discard group={getattr(self, 'group_name', None)} channel={self.channel_name}"
            )
            if had_group:
                await self.channel_layer.group_discard(self.group_name, self.channel_name)
        except Exception as e:
            log.warning(f"[WS][crud][disconnect][warn] {e}")
        finally:
            elapsed = time.time() - start
            log.info(f"[WS][crud][disconnect] code={close_code} elapsed={elapsed:.3f}s")

    async def receive(self, text_data=None, bytes_data=None):
        # Este consumer es solo para enviar eventos desde el backend
        pass

    async def crud_event(self, event):
        # Enviar el evento al frontend
        await self.send(text_data=json.dumps(event["data"]))
