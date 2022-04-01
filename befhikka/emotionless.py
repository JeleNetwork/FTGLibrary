"""
    █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
    █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█

    Copyright 2022 t.me/hikariatama
    Licensed under the Creative Commons CC BY-NC-ND 4.0

    Full license text can be found at:
    https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode

    Human-friendly one:
    https://creativecommons.org/licenses/by-nc-nd/4.0
"""

# meta pic: https://img.icons8.com/external-vitaliy-gorbachev-flat-vitaly-gorbachev/58/000000/external-sad-social-media-vitaliy-gorbachev-flat-vitaly-gorbachev.png
# meta developer: @hikariatama
# scope: geektg_min 3.1.17
# scope: geektg_only
# requires: telethon-mod

from .. import loader, utils
from telethon.tl.types import Message
from telethon.events import Raw
from telethon.tl.types import UpdateMessageReactions
from telethon.tl.functions.messages import ReadReactionsRequest
from telethon.utils import get_input_peer
import logging
import asyncio
import time

logger = logging.getLogger(__name__)


@loader.tds
class EmotionlessMod(loader.Module):
    """Automatically reads reactions"""

    strings = {"name": "Emotionless", "state": "😑 <b>Emotionless mode is now {}</b>"}

    def get(self, *args) -> dict:
        return self._db.get(self.strings["name"], *args)

    def set(self, *args) -> None:
        return self._db.set(self.strings["name"], *args)

    async def client_ready(self, client, db) -> None:
        self._db = db
        self._client = client
        self._flood_protect = []
        self._queue = {}
        self._flood_protect_sample = 60
        self._threshold = 10

        self.handler = (self._handler, Raw)
        client.add_event_handler(*self.handler)
        self._task = asyncio.ensure_future(self._queue_handler())

    async def on_unload(self) -> None:
        self._client.remove_event_handler(*self.handler)
        self._task.cancel()

    async def noreactscmd(self, message: Message) -> None:
        """Toggle reactions auto-reader"""
        state = not self.get("state", False)
        self.set("state", state)
        await utils.answer(
            message, self.strings("state").format("on" if state else "off")
        )

    async def _queue_handler(self) -> None:
        while True:

            for chat, schedule in self._queue.copy().items():
                if schedule < time.time():
                    await self._client(ReadReactionsRequest(get_input_peer(chat)))
                    logger.debug(f"Read reactions in queued peer {chat}")
                    del self._queue[chat]

            await asyncio.sleep(5)

    async def _handler(self, event: Raw) -> None:
        try:
            if not isinstance(event, UpdateMessageReactions):
                return

            if not self.get("state", False):
                return

            if (
                not hasattr(event, "reactions")
                or not hasattr(event.reactions, "recent_reactions")
                or not isinstance(event.reactions.recent_reactions, (list, set, tuple))
                or not any(i.unread for i in event.reactions.recent_reactions)
            ):
                return

            self._flood_protect = list(filter(lambda x: x > time.time(), self._flood_protect))

            if len(self._flood_protect) > self._threshold:
                self._queue[utils.get_chat_id(event)] = time.time() + 15
                logger.debug(f"Flood protect triggered, chat {event} added to queue")
                return

            self._flood_protect += [round(time.time()) + self._flood_protect_sample]

            await self._client(ReadReactionsRequest(event.peer))
            logger.debug(f"Read reaction in {event.peer}")
        except Exception:
            logger.exception("Caught exception in Emotionless")
