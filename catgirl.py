__version__ = (1, 0, 0)
"""
    █   █ █   █ █ █ █▀█ █▄ █ █▄▀ ▄▀█
    █▄▄ █ █▄▄ ▀▄▀▄▀ █▄█ █ ▀█ █ █ █▀█

    Copyright 2022 t.me/lil_wonka
    Licensed under the Creative Commons CC BY-NC-ND 4.0

    Full license text can be found at:
    https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode

    Human-friendly one:
    https://creativecommons.org/licenses/by-nc-nd/4.0
"""

# meta pic: https://img.icons8.com/external-flaticons-lineal-color-flat-icons/48/000000/external-anime-addiction-flaticons-lineal-color-flat-icons.png
# Sends cute anime girl pictures


from .. import loader, utils
from telethon.tl.types import Message
import logging
import requests
from random import choice
from aiogram.types import CallbackQuery

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

# requires: requests
# score: inline

logger = logging.getLogger(__name__)


@loader.tds
class CatgirlMod(loader.Module):
    """Sends cute anime girl pictures
    remaked @hikarimods module Catboys
    """

    strings = {"name": "Catgirl"}

    def get(self, *args) -> dict:
        return self.db.get(self.strings["name"], *args)

    def set(self, *args) -> None:
        return self.db.set(self.strings["name"], *args)

    async def client_ready(self, client, db) -> None:
        self.db = db
        self.client = client

    async def inline__choice(self, call, type):
        self.set("type", type)
        type = {
            "nsfw": "🔞 With nsfw",
            "random": "💞 Random",
            "without": "✅ Without nsfw",
        }[type]
        return await call.edit(
            "🦊 Choose pictures type:\n" f"Current: {type}",
            reply_markup=[
                [
                    {
                        "text": "🔞 With nsfw",
                        "callback": self.inline__choice,
                        "args": ("nsfw",),
                    }
                ],
                [
                    {
                        "text": "💞 Random",
                        "callback": self.inline__choice,
                        "args": ("random",),
                    }
                ],
                [
                    {
                        "text": "✅ Without nsfw",
                        "callback": self.inline__choice,
                        "args": ("without",),
                    }
                ],
            ],
        )

    async def inline__back(self, call, chat, msg_id, url):
        caption = f"<i>{choice(phrases)}</i> {choice(faces)}"
        self.set("url", url)
        try:
            await self.client.edit_message(chat, msg_id, file=url)
        except:
            return await call.answer()
        await call.edit(
            caption,
            reply_markup=[
                [
                    {
                        "text": "🎲 Next",
                        "callback": self.inline__next,
                        "args": (chat, msg_id),
                    },
                ],
            ],
        )

    async def inline__next(self, call: CallbackQuery, chat: int, msg_id: int) -> None:
        choose = self.get("type")
        if not choose:
            self.set("type", "random")
        n = {"nsfw": "?nsfw=true", "without": "?nsfw=false", "random": ""}[choose]
        for i in range(100):
            try:
                x = requests.get("https://nekos.moe/api/v1/random/image" + n).json()[
                    "images"
                ][0]
                break
            except:
                pass
        url = f'https://nekos.moe/image/{x["id"]}.jpg'
        caption = f"<i>{choice(phrases)}</i> {choice(faces)}"
        try:
            await self.client.edit_message(chat, msg_id, file=url)
        except:
            return await call.answer()
        await call.edit(
            caption,
            reply_markup=[
                [
                    {
                        "text": "🎲 Next",
                        "callback": self.inline__next,
                        "args": (chat, msg_id),
                    },
                ],
                [
                    {
                        "text": "🎲 Back",
                        "callback": self.inline__back,
                        "args": (chat, msg_id, self.get("url")),
                    }
                ],
            ],
        )
        self.set("url", url)

    async def catgirlcmd(self, message: Message) -> None:
        """Send catgirl picture"""
        choose = self.get("type")
        if not choose:
            choose = "random"
            self.set("type", choose)
        n = {"nsfw": "?nsfw=true", "without": "?nsfw=false", "random": ""}[choose]
        for i in range(100):
            try:
                x = requests.get("https://nekos.moe/api/v1/random/image" + n).json()[
                    "images"
                ][0]
                break
            except:
                pass
        url = f'https://nekos.moe/image/{x["id"]}.jpg'
        self.set("url", url)
        await message.delete()

        caption = f"<i>{choice(phrases)}</i> {choice(faces)}"

        if not hasattr(self, "inline") or not self.inline.init_complete:
            for i in range(10):
                try:
                    await self.client.send_file(
                        message.peer_id,
                        url,
                        caption=caption,
                        reply_to=message.reply_to_msg_id,
                    )
                    break
                except:
                    pass
                return await utils.answer(message, "Error while sending photo...")
        else:
            m = "sex"
            for i in range(10):
                try:
                    m = await self.client.send_file(
                        message.peer_id, url, reply_to=message.reply_to_msg_id
                    )
                    break
                except:
                    pass
            if m == "sex":
                return await utils.answer(message, "Error while sending photo...")
            await self.inline.form(
                caption,
                message=message,
                reply_markup=[
                    [
                        {
                            "text": "🎲 Next",
                            "callback": self.inline__next,
                            "args": (utils.get_chat_id(m), m.id),
                        }
                    ]
                ],
                ttl=15 * 60,
            )

    async def setpictypecmd(self, m: Message):
        """Choose type of catgirl pictures"""
        choosed = self.get("type")
        if not choosed:
            choosed = "random"
            self.set("type", choosed)
        type = {
            "nsfw": "🔞 With nsfw",
            "random": "💞 Random",
            "without": "✅ Without nsfw",
        }[choosed]
        return await self.inline.form(
            "🦊 Choose pictures type:\n" f"Current: {type}",
            message=m,
            reply_markup=[
                [
                    {
                        "text": "🔞 With nsfw",
                        "callback": self.inline__choice,
                        "args": ("nsfw",),
                    }
                ],
                [
                    {
                        "text": "💞 Random",
                        "callback": self.inline__choice,
                        "args": ("random",),
                    }
                ],
                [
                    {
                        "text": "✅ Without nsfw",
                        "callback": self.inline__choice,
                        "args": ("without",),
                    }
                ],
            ],
        )
