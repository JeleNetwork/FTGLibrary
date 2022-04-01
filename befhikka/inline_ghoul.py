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

# meta pic: https://img.icons8.com/fluency/48/000000/dota.png
# meta developer: @hikariatama
# scope: inline
# scope: geektg_only

from .. import loader
from telethon.tl.types import Message
from aiogram.types import CallbackQuery
import logging
import asyncio

logger = logging.getLogger(__name__)


@loader.tds
class InlineGhoulMod(loader.Module):
    """Non-spammy ghoul module"""

    strings = {
        "name": "InlineGhoul",
        "iamghoul": "🧐 <b>Who am I?</b>",
        "tired": "😾 <b>I'm tired to count!</b>",
    }

    def get(self, *args) -> dict:
        return self.db.get(self.strings["name"], *args)

    def set(self, *args) -> None:
        return self.db.set(self.strings["name"], *args)

    async def client_ready(self, client, db) -> None:
        self.db = db
        self.client = client

    async def inline_close(self, call: CallbackQuery) -> None:
        await call.close()

    async def inline__handler(self, call: CallbackQuery, correct: bool) -> None:
        if not correct:
            await call.answer("NO!")
            return

        x = 1000
        while x > 900:
            await call.edit(f"👊 <b>{x} - 7 = {x - 7}</b>")
            x -= 7
            await asyncio.sleep(1)

        await call.edit(self.strings("tired"))
        await asyncio.sleep(10)
        await call.edit(
            self.strings("tired"),
            reply_markup=[[{"text": "💔 Хочу также!", "url": "https://t.me/chat_ftg"}]],
        )
        await call.unload()

    async def ghoulcmd(self, message: Message) -> None:
        """Sends ghoul message"""
        await self.inline.form(
            self.strings("iamghoul"),
            message=message,
            reply_markup=[
                [
                    {
                        "text": "🧠 Ghoul",
                        "callback": self.inline__handler,
                        "args": (True,),
                    },
                    {
                        "text": "💃 Ballerina",
                        "callback": self.inline__handler,
                        "args": (False,),
                    },
                ]
            ],
            force_me=False,
        )
