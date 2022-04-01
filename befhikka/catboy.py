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

# meta pic: https://img.icons8.com/color/48/000000/neko-boy.png
# meta developer: @hikariatama
# scope: geektg_min 3.1.22
# requires: requests

from .. import loader, utils
from telethon.tl.types import Message
import requests
from random import choice

phrases = ["Uwu", "Senpai", "Uff", "Meow", "Bonk", "Ara-ara", "Hewwo", "You're cute!"]

faces = [
    "ʕ•ᴥ•ʔ",
    "(ᵔᴥᵔ)",
    "(◕‿◕✿)",
    "(づ￣ ³￣)づ",
    "♥‿♥",
    "~(˘▾˘~)",
    "(｡◕‿◕｡)",
    "｡◕‿◕｡",
    "ಠ‿↼",
]


async def photo() -> str:
    return (await utils.run_sync(requests.get, "https://api.catboys.com/img")).json()[
        "url"
    ]


@loader.tds
class CatboyMod(loader.Module):
    """Sends cute anime boy pictures"""

    strings = {"name": "Catboy"}

    async def client_ready(self, client, db) -> None:
        self._client = client

    async def catboycmd(self, message: Message) -> None:
        """Send catboy picture"""
        if not hasattr(self, "inline") or not self.inline.init_complete:
            await self._client.send_file(
                message.peer_id,
                await photo(),
                caption=f"<i>{choice(phrases)}</i> {choice(faces)}",
                reply_to=message.reply_to_msg_id,
            )
            await message.delete()
        else:
            await self.inline.gallery(
                caption=lambda: f"<i>{choice(phrases)}</i> {choice(faces)}",
                message=message,
                next_handler=photo,
            )
