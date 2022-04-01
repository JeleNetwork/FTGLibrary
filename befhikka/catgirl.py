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

# meta pic: https://img.icons8.com/external-justicon-flat-justicon/344/external-cat-animal-justicon-flat-justicon.png
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
    tag = "nsfw"
    while tag == "nsfw":
        img = (
            await utils.run_sync(requests.get, "https://nekos.moe/api/v1/random/image")
        ).json()["images"][0]
        tag = "nsfw" if img["nsfw"] else "sfw"

    return f'https://nekos.moe/image/{img["id"]}.jpg'


@loader.tds
class CatgirlMod(loader.Module):
    """Sends cute anime girl pictures"""

    strings = {"name": "Catgirl"}

    async def client_ready(self, client, db) -> None:
        self._client = client

    async def catgirlcmd(self, message: Message) -> None:
        """Send catgirl picture"""
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
