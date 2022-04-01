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

# meta pic: https://img.icons8.com/fluency/50/000000/event-log.png
# meta developer: @hikariatama

from .. import loader, utils, main
import logging
from telethon.tl.functions.channels import CreateChannelRequest

logger = logging.getLogger(__name__)


@loader.tds
class OnloadExecutorMod(loader.Module):
    """Executes selected commands after every userbot restart"""

    strings = {"name": "OnloadExecutor"}

    async def client_ready(self, client, db) -> None:
        self.db = db
        self.client = client
        self._me = (await client.get_me()).id

        self.c = await self.find_db()
        self.prefix = utils.escape_html(
            (db.get(main.__name__, "command_prefix", False) or ".")[0]
        )

        async for message in client.iter_messages(self.c):
            if (getattr(message, "raw_text", "") or "").startswith(self.prefix):
                try:
                    m = await client.send_message("me", message.raw_text)
                    await self.allmodules.commands[message.raw_text[1:].split()[0]](m)
                    logger.info("Registered onload command")
                    await m.delete()
                except Exception:
                    logger.exception(
                        f"Exception while executing command {message.raw_text[:15]}..."
                    )

    async def find_db(self):
        async for d in self.client.iter_dialogs():
            if d.title == f"onload-commands-{self._me}":
                return d.entity

        return (
            await self.client(
                CreateChannelRequest(
                    f"onload-commands-{self._me}",
                    "All commands from this chat will be executed once FTG is started, be careful!",
                    megagroup=True,
                )
            )
        ).chats[0]
