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

# meta pic: https://img.icons8.com/fluency/48/000000/why-us-female.png
# meta developer: @hikariatama

from .. import loader, utils
from telethon.tl.types import Message
import logging

logger = logging.getLogger(__name__)


@loader.tds
class TelethonDocsMod(loader.Module):
    """Simple mod to quickly access telethon docs"""

    strings = {"name": "TelethonDocs"}

    async def client_ready(self, client, db) -> None:
        self.db = db
        self.client = client

    async def watcher(self, message: Message) -> None:
        if not getattr(message, "raw_text", None):
            return

        if not message.out or (
            not message.raw_text.startswith("#client")
            and not message.raw_text.startswith("#ref")
        ):
            return

        async with self.client.conversation("@nekoboy_telethon_bot") as conv:
            m = await conv.send_message(message.raw_text)
            r = await conv.get_response()

            await utils.answer(message, r.text)
            await m.delete()
            await r.delete()
