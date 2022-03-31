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

# meta pic: https://img.icons8.com/fluency/48/000000/logbook.png
# meta developer: @hikariatama
# scope: geektg_only

from .. import loader, utils, main
from telethon.tl.functions.channels import CreateChannelRequest
import logging
import telethon.utils as tutils
from telethon.tl.types import Message

logger = logging.getLogger(__name__)


@loader.tds
class CommandsLoggerMod(loader.Module):
    """Log any evaluated commands"""

    strings = {"name": "CommandsLogger"}

    async def find_db(self):
        async for d in self.client.iter_dialogs():
            if d.title == "geektg-log":
                return d.entity

        return (
            await self.client(
                CreateChannelRequest(
                    "geektg-log", "Commands will appear there", megagroup=True
                )
            )
        ).chats[0]

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        try:
            self.geektg_ver = main.__version__
        except Exception as e:
            raise Exception("This module is supported only by GeekTG") from e

        if self.geektg_ver < (2, 0, 2):
            raise Exception(
                "Module is not supported in your version of GeekTG. Please, update"
            )

        self.log_channel = await self.find_db()
        self.prefix = utils.escape_html(
            (self.db.get(main.__name__, "command_prefix", False) or ".")[0]
        )
        loader.mods = self.allmodules.modules

        logger.warning("Logging installed")

    async def process_log(self, message: Message) -> None:
        try:
            by = (
                f'\n<b>By: <a href="tg://user?id={message.sender.id}">{tutils.get_display_name(message.sender)}</a></b>'
                if not message.out
                else ""
            )
        except AttributeError:
            by = (
                f'\n<b>By: <a href="tg://user?id={message.chat_id}">{tutils.get_display_name(await self.client.get_entity(message.chat_id))}</a> in pm</b>'
                if not message.out
                else ""
            )

        await self.client.send_message(
            self.log_channel, f"<code>{self.prefix}{message.raw_text}</code>{by}"
        )
