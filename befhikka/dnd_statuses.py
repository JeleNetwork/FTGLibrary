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

# meta pic: https://img.icons8.com/fluency/48/000000/envelope-number.png
# meta developer: @hikariatama

from .. import loader, utils
import asyncio
from telethon import types
from telethon.tl.types import Message
import logging

logger = logging.getLogger(__name__)


@loader.tds
class StatusesMod(loader.Module):
    """AFK Module analog with extended functionality"""

    strings = {
        "name": "Statuses",
        "status_not_found": "<b>🦊 Status not found</b>",
        "status_set": "<b>🦊 Status set\n</b><code>{}</code>\nNotify: {}",
        "pzd_with_args": "<b>🦊 Args are incorrect</b>",
        "status_created": "<b>🦊 Status {} created\n</b><code>{}</code>\nNotify: {}",
        "status_removed": "<b>🦊 Status {} deleted</b>",
        "no_status": "<b>🦊 No status is active</b>",
        "status_unset": "<b>🦊 Status removed</b>",
        "available_statuses": "<b>🦊 Available statuses:</b>\n\n",
    }

    async def client_ready(self, client, db):
        self.db = db
        self.client = client
        self._me = await client.get_me(True)
        self._ratelimit = []
        self._sent_messages = []

    async def watcher(self, message: Message) -> None:
        if not isinstance(message, types.Message):
            return

        if not self.db.get("Statuses", "status", False):
            return

        if getattr(message.to_id, "user_id", None) == self._me.user_id:
            user = await utils.get_user(message)
            if user in self._ratelimit:
                return

            if user.is_self or user.bot or user.verified:
                return
        elif not message.mentioned:
            return

        chat = utils.get_chat_id(message)

        if chat in self._ratelimit:
            return

        m = await utils.answer(
            message,
            self.db.get("Statuses", "texts", {"": ""})[
                self.db.get("Statuses", "status", "")
            ],
        )

        if isinstance(m, (list, tuple, set)):
            m = m[0]

        self._sent_messages += [m]

        if not self.db.get("Statuses", "notif", {"": False})[
            self.db.get("Statuses", "status", "")
        ]:
            await message.client.send_read_acknowledge(
                message.chat_id, clear_mentions=True
            )

        self._ratelimit.append(chat)

    async def statuscmd(self, message: Message) -> None:
        """<short_name> - Set status"""
        args = utils.get_args_raw(message)
        if args not in self.db.get("Statuses", "texts", {}):
            await utils.answer(message, self.strings("status_not_found", message))
            await asyncio.sleep(3)
            await message.delete()
            return

        self.db.set("Statuses", "status", args)
        self._ratelimit = []
        await utils.answer(
            message,
            self.strings("status_set", message).format(
                utils.escape_html(self.db.get("Statuses", "texts", {})[args]),
                str(self.db.get("Statuses", "notif")[args]),
            ),
        )

    async def newstatuscmd(self, message: Message) -> None:
        """<short_name> <notif|0/1> <text> - New status
        Example: .newstatus test 1 Hello!"""
        args = utils.get_args_raw(message)
        args = args.split(" ", 2)
        if len(args) < 3:
            await utils.answer(message, self.strings("pzd_with_args", message))
            await asyncio.sleep(3)
            await message.delete()
            return

        args[1] = args[1] in ["1", "true", "yes", "+"]
        texts = self.db.get("Statuses", "texts", {})
        texts[args[0]] = args[2]
        self.db.set("Statuses", "texts", texts)

        notif = self.db.get("Statuses", "notif", {})
        notif[args[0]] = args[1]
        self.db.set("Statuses", "notif", notif)
        await utils.answer(
            message,
            self.strings("status_created", message).format(
                utils.escape_html(args[0]), utils.escape_html(args[2]), args[1]
            ),
        )

    async def delstatuscmd(self, message: Message) -> None:
        """<short_name> - Delete status"""
        args = utils.get_args_raw(message)
        if args not in self.db.get("Statuses", "texts", {}):
            await utils.answer(message, self.strings("status_not_found", message))
            await asyncio.sleep(3)
            await message.delete()
            return

        texts = self.db.get("Statuses", "texts", {})
        del texts[args]
        self.db.set("Statuses", "texts", texts)

        notif = self.db.get("Statuses", "notif", {})
        del notif[args]
        self.db.set("Statuses", "notif", notif)
        await utils.answer(
            message,
            self.strings("status_removed", message).format(utils.escape_html(args)),
        )

    async def unstatuscmd(self, message: Message) -> None:
        """Remove status"""
        if not self.db.get("Statuses", "status", False):
            await utils.answer(message, self.strings("no_status", message))
            await asyncio.sleep(3)
            await message.delete()
            return

        self.db.set("Statuses", "status", False)
        self._ratelimit = []

        for m in self._sent_messages:
            try:
                await m.delete()
            except Exception:
                logger.exception("Message not deleted due to")

        self._sent_messages = []

        await utils.answer(message, self.strings("status_unset", message))

    async def statusescmd(self, message: Message) -> None:
        """Show available statuses"""
        res = self.strings("available_statuses", message)
        for short_name, status in self.db.get("Statuses", "texts", {}).items():
            res += f"<b><u>{short_name}</u></b> | Notify: <b>{self.db.get('Statuses', 'notif', {})[short_name]}</b>\n{status}\n➖➖➖➖➖➖➖➖➖\n"

        await utils.answer(message, res)
