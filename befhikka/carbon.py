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

# meta pic: https://img.icons8.com/fluency/48/000000/code.png
# meta developer: @hikariatama

from .. import loader, utils

import requests
import logging
from telethon.tl.types import Message

# requires: urllib requests

logger = logging.getLogger(__name__)


@loader.tds
class CarbonMod(loader.Module):
    """Create beautiful code images"""

    strings = {
        "name": "Carbon",
        "args": "🦊 <b>No args specified</b>",
        "loading": "🦊 <b>Loading...</b>",
    }

    async def client_ready(self, client, db):
        self.client = client

    @loader.unrestricted
    async def carboncmd(self, message: Message) -> None:
        """<code> - Сделать красивую фотку кода"""
        args = utils.get_args_raw(message)

        try:
            code_from_message = (await self.client.download_file(message.media)).decode(
                "utf-8"
            )
        except Exception:
            code_from_message = ""

        try:
            reply = await message.get_reply_message()
            code_from_reply = (await self.client.download_file(reply.media)).decode(
                "utf-8"
            )
        except Exception:
            code_from_reply = ""

        args = args or code_from_message or code_from_reply

        message = await utils.answer(message, self.strings("loading", message))
        try:
            message = message[0]
        except Exception:
            pass

        await self.client.send_message(
            utils.get_chat_id(message),
            file=(
                await utils.run_sync(
                    requests.post,
                    "https://carbonara-42.herokuapp.com/api/cook",
                    json={"code": args},
                )
            ).content,
        )
        await message.delete()
