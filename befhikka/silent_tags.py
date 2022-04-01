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

# meta pic: https://img.icons8.com/fluency/48/000000/witch.png
# meta developer: @hikariatama

from .. import loader, utils
from telethon.tl.functions.channels import CreateChannelRequest
import logging
import asyncio
from telethon.tl.types import Message

logger = logging.getLogger(__name__)


@loader.tds
class SilentTagsMod(loader.Module):
    """Mutes tags and logs them"""

    strings = {
        "name": "SilentTags",
        "tagged": '<b>👋🏻 You were tagged in <a href="{}">{}</a> by <a href="tg://user?id={}">{}</a></b>\n<code>Message:</code>\n{}\n<b>Link: <a href="https://t.me/c/{}/{}">click</a></b>',
        "tag_mentioned": "<b>👾 Silent Tags are active</b>",
        "stags_status": "<b>👾 Silent Tags are {}</b>",
    }

    async def find_db(self):
        async for d in self.client.iter_dialogs():
            if d.title == "silent-tags-log":
                return d.entity

        return (
            await self.client(
                CreateChannelRequest(
                    "silent-tags-log",
                    f"Messages with @{self.un} will appear here",
                    megagroup=True,
                )
            )
        ).chats[0]

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.stags = db.get("SilentTags", "stags", False)
        self.un = (await client.get_me()).username
        self._ratelimit = []
        if self.un is None:
            raise Exception(
                "You cannot load this module because you do not have username"
            )
        self.c = await self.find_db()

    async def stagscmd(self, message: Message) -> None:
        """<on\\off> - Toggle notifications about tags"""
        args = utils.get_args_raw(message)

        if args not in ["on", "off"]:
            await utils.answer(
                message,
                self.strings("stags_status", message).format(
                    "active" if self.stags else "inactive"
                ),
            )
            return

        args = args == "on"
        self.db.set("SilentTags", "stags", args)
        self.stags = args
        self._ratelimit = []
        await utils.answer(
            message,
            self.strings("stags_status").format(
                "now on" if args else "now off", message
            ),
        )

    async def watcher(self, message: Message) -> None:
        try:
            if message.mentioned and self.stags:
                await self.client.send_read_acknowledge(
                    message.chat_id, clear_mentions=True
                )
                cid = utils.get_chat_id(message)

                if message.is_private:
                    ctitle = "pm"
                else:
                    chat = await message.get_chat()
                    grouplink = (
                        f"https://t.me/{chat.username}"
                        if getattr(chat, "username", None) is not None
                        else ""
                    )
                    ctitle = chat.title

                uid = message.from_id

                try:
                    user = await self.client.get_entity(message.from_id)
                    uname = user.first_name
                except Exception:
                    uname = "Unknown user"

                await self.client.send_message(
                    self.c,
                    self.strings("tagged").format(
                        grouplink, ctitle, uid, uname, message.text, cid, message.id
                    ),
                    link_preview=False,
                )
                if cid not in self._ratelimit:
                    self._ratelimit.append(cid)
                    ms = await utils.answer(message, self.strings("tag_mentioned"))
                    ms = ms[0] if isinstance(ms, list) else ms
                    await asyncio.sleep(5)
                    await ms.delete()
        except Exception:
            pass
