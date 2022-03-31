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

# meta pic: https://img.icons8.com/fluency/48/000000/anime.png
# meta developer: @hikariatama

from .. import loader, utils
import requests
import json
from urllib.parse import quote_plus
import asyncio
from telethon.tl.types import Message

# requires: urllib requests


def chunks(lst, n):
    return [lst[i : i + n] for i in range(0, len(lst), n)]


@loader.tds
class NekosLifeMod(loader.Module):
    """NekosLife API Wrapper"""

    strings = {"name": "NekosLife"}

    async def client_ready(self, client, db):
        self.client = client
        ans = (
            await utils.run_sync(requests.get, "https://nekos.life/api/v2/endpoints")
        ).json()
        self.categories = json.loads(
            "["
            + [_ for _ in ans if "/api" in _ and "/img/" in _][0]
            .split("<")[1]
            .split(">")[0]
            .replace("'", '"')
            + "]"
        )
        self.endpoints = {
            "img": "https://nekos.life/api/v2/img/",
            "owoify": "https://nekos.life/api/v2/owoify?text=",
            "why": "https://nekos.life/api/v2/why",
            "cat": "https://nekos.life/api/v2/cat",
            "fact": "https://nekos.life/api/v2/fact",
        }

    @loader.pm
    async def nkcmd(self, message: Message) -> None:
        """Send anime pic"""
        args = utils.get_args_raw(message)
        args = "neko" if args not in self.categories else args
        pic = (
            await utils.run_sync(requests.get, f"{self.endpoints['img']}{args}")
        ).json()["url"]
        await self.client.send_file(
            message.peer_id, pic, reply_to=message.reply_to_msg_id
        )
        await message.delete()

    @loader.pm
    async def nkctcmd(self, message: Message) -> None:
        """Show available categories"""
        cats = "\n".join(
            [" | </code><code>".join(_) for _ in chunks(self.categories, 5)]
        )
        await utils.answer(
            message, f"<b>Available categories:</b>\n<code>{cats}</code>"
        )

    @loader.unrestricted
    async def owoifycmd(self, message: Message) -> None:
        """OwOify text"""
        args = utils.get_args_raw(message)
        if not args:
            args = await message.get_reply_message()
            if not args:
                await message.delete()
                return

            args = args.text

        if len(args) > 180:
            message = await utils.answer(message, "<b>OwOifying...</b>")
            try:
                message = message[0]
            except Exception:
                pass

        args = quote_plus(args)
        owo = ""
        for chunk in chunks(args, 180):
            owo += (
                await utils.run_sync(requests.get, f"{self.endpoints['owoify']}{chunk}")
            ).json()["owo"]
            await asyncio.sleep(0.1)
        await utils.answer(message, owo)

    @loader.unrestricted
    async def whycmd(self, message: Message) -> None:
        """Why?"""
        await utils.answer(
            message,
            f"<code>👾 {(await utils.run_sync(requests.get, self.endpoints['why'])).json()['why']}</code>",
        )

    @loader.unrestricted
    async def factcmd(self, message: Message) -> None:
        """Did you know?"""
        await utils.answer(
            message,
            f"<b>🧐 Did you know, that </b><code>{(await utils.run_sync(requests.get, self.endpoints['fact'])).json()['fact']}</code>",
        )

    @loader.unrestricted
    async def meowcmd(self, message: Message) -> None:
        """Sends cat ascii art"""
        await utils.answer(
            message,
            f"<b>{(await utils.run_sync(requests.get, self.endpoints['cat'])).json()['cat']}</b>",
        )
