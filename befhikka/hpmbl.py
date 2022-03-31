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

# meta title: PM->BL
# meta pic: https://img.icons8.com/fluency/48/000000/poison.png
# meta developer: @hikariatama

from .. import loader, utils
from telethon.tl.types import Message, PeerUser, User
import logging
from telethon.tl.functions.contacts import BlockRequest
from telethon.tl.functions.messages import DeleteHistoryRequest, ReportSpamRequest
import time
from telethon.utils import get_peer_id, get_display_name
import requests
import io
from typing import Union

logger = logging.getLogger(__name__)


guard_pic = io.BytesIO(
    requests.get(
        "https://i.pinimg.com/originals/a4/3e/09/a43e092c3b5f37fe84a0e2173c82dc35.jpg"
    ).content
)
guard_pic.name = "picture.png"


def format_(state: Union[bool, None]) -> str:
    if state is None:
        return "❔"

    return "✅" if state else "🚫 Not"


@loader.tds
class PMBLMod(loader.Module):
    """Bans and reports incoming messages from unknown users"""

    strings = {
        "name": "PMBL",
        "state": "📴 <b>PM->BL is now {}</b>\n<i>Report spam? - {}\nDelete dialog? - {}</i>",
        "args": "ℹ️ <b>Example usage: </b><code>.pmblsett 0 0</code>",
        "args_pmban": "ℹ️ <b>Example usage: </b><code>.pmbanlast 5</code>",
        "config": "😶‍🌫️ <b>Yeiks! Config saved</b>\n<i>Report spam? - {}\nDelete dialog? - {}</i>",
        "banned": "🤵 <b>Please, wait •ᴗ•</b>\nI'm the <b>guardian</b> of this account and you are <b>not approved</b>! You can contact my owner <b>in chat</b>, if you need help.\n<b>Sorry, but I need to ban you in terms of security</b> 😥",
        "removing": "😶‍🌫️ <b>Removing {} last dialogs...</b>",
        "removed": "😶‍🌫️ <b>Removed {} last dialogs!</b>",
        "user_not_specified": "🚫 <b>You haven't specified user</b>",
        "approved": '😶‍🌫️ <b><a href="tg://user?id={}">{}</a> approved in pm</b>',
        "banned_log": '👮 <b>I banned <a href="tg://user?id={}">{}</a>.</b>\n\n<b>{} Contact</b>\n<b>{} Started by you</b>\n<b>{} Active conversation</b>\n\n<b>✊ Actions</b>\n\n<b>{} Reported spam</b>\n<b>{} Deleted dialog</b>\n<b>{} Banned</b>\n\n<b>ℹ️ Message</b>\n<code>{}</code>',
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            "ignore_contacts",
            True,
            lambda: "Ignore contacts?",
            #
            "ignore_active",
            True,
            lambda: "Ignore peers, where you participated?",
            #
            "active_threshold",
            5,
            lambda: "What number of your messages is required to trust peer",
            #
            "custom_message",
            "",
            lambda: "Custom message to notify untrusted peers. Leave empty for default one",
        )

    def get(self, *args) -> dict:
        return self.db.get(self.strings["name"], *args)

    def set(self, *args) -> None:
        return self.db.set(self.strings["name"], *args)

    async def client_ready(self, client, db) -> None:
        self.db = db
        self.client = client
        self._whitelist = self.get("whitelist", [])
        self._me = (await client.get_me()).id
        self._ratelimit = []
        self._ratelimit_timeout = 5 * 60
        self._ratelimit_threshold = 10

    async def pmblcmd(self, message: Message) -> None:
        """Toggle PMAntiRaid"""
        current = self.get("state", False)
        new = not current
        self.set("state", new)
        await utils.answer(
            message,
            self.strings("state").format(
                "on" if new else "off",
                "yes" if self.get("spam", False) else "no",
                "yes" if self.get("delete", False) else "no",
            ),
        )

    async def pmblsettcmd(self, message: Message) -> None:
        """<report spam?> <delete dialog?> - Configure PMAntiRaid - all params are 1/0"""
        args = utils.get_args(message)
        if not args or len(args) != 2 or any(not _.isdigit() for _ in args):
            await utils.answer(message, self.strings("args"))
            return

        spam, delete = list(map(int, args))
        self.set("spam", spam)
        self.set("delete", delete)
        await utils.answer(
            message,
            self.strings("config").format(
                "yes" if spam else "no",
                "yes" if delete else "no",
            ),
        )

    async def pmbanlastcmd(self, message: Message) -> None:
        """<number> - Ban and delete dialogs with n most new users"""
        n = utils.get_args_raw(message)
        if not n or not n.isdigit():
            await utils.answer(message, self.strings("args_pmban"))
            return

        n = int(n)

        await utils.answer(message, self.strings("removing").format(n))

        dialogs = []
        async for dialog in self.client.iter_dialogs(ignore_pinned=True):
            try:
                if not isinstance(dialog.message.peer_id, PeerUser):
                    continue
            except AttributeError:
                continue

            m = (
                await self.client.get_messages(
                    dialog.message.peer_id, limit=1, reverse=True
                )
            )[0]

            dialogs += [
                (
                    get_peer_id(dialog.message.peer_id),
                    int(time.mktime(m.date.timetuple())),
                )
            ]

        dialogs.sort(key=lambda x: x[1])
        to_ban = [d for d, _ in dialogs[::-1][:n]]

        for d in to_ban:
            await self.client(BlockRequest(id=d))

            await self.client(DeleteHistoryRequest(peer=d, just_clear=True, max_id=0))

        await utils.answer(message, self.strings("removed").format(n))

    def _approve(self, user: int, reason: str = "unknown") -> None:
        self._whitelist += [user]
        self._whitelist = list(set(self._whitelist))
        self.set("whitelist", self._whitelist)
        logger.info(f"User approved in pm {user}, filter: {reason}")
        return

    async def allowpmcmd(self, message: Message) -> None:
        """<reply or user> - Allow user to pm you"""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()

        user = None

        try:
            user = await self.client.get_entity(args)
        except Exception:
            try:
                user = await self.client.get_entity(reply.sender_id) if reply else None
            except Exception:
                pass

        if not user:
            chat = await message.get_chat()
            if not isinstance(chat, User):
                await utils.answer(message, self.strings("user_not_specified"))
                return

            user = chat

        self._approve(user.id, "manual_approve")
        await utils.answer(
            message, self.strings("approved").format(user.id, get_display_name(user))
        )

    async def watcher(self, message: Message) -> None:
        if getattr(message, "out", False):
            return

        if not isinstance(message, Message):
            return

        if not isinstance(message.peer_id, PeerUser):
            return

        if not self.get("state", False):
            return

        cid = utils.get_chat_id(message)
        if cid in self._whitelist:
            return

        contact, started_by_you, active_peer = None, None, None

        first_message = (
            await self.client.get_messages(message.peer_id, limit=1, reverse=True)
        )[0]

        if getattr(message, 'raw_text', False) and first_message.sender_id == self._me:
            return self._approve(cid, "started_by_you")
        else:
            started_by_you = False

        try:
            if self.config["ignore_contacts"]:
                if (await self.client.get_entity(message.peer_id)).contact:
                    return self._approve(cid, "ignore_contacts")
                else:
                    contact = False
        except ValueError:
            # If we were not able to resolve entity
            # user is not a contact. So just ignore
            # this exception
            pass

        if self.config["ignore_active"]:
            q = 0

            async for msg in self.client.iter_messages(message.peer_id, limit=200):
                if msg.sender_id == self._me:
                    q += 1

                if q >= self.config["active_threshold"]:
                    return self._approve(cid, "active_threshold")

            active_peer = False

        self._ratelimit = list(
            filter(lambda x: x + self._ratelimit_timeout < time.time(), self._ratelimit)
        )

        if len(self._ratelimit) < self._ratelimit_threshold:
            try:
                await self.client.send_file(
                    message.peer_id,
                    guard_pic,
                    caption=self.config["custom_message"] or self.strings("banned"),
                )
            except Exception:
                await utils.answer(
                    message, self.config["custom_message"] or self.strings("banned")
                )

            self._ratelimit += [round(time.time())]

            try:
                peer = await self.client.get_entity(message.peer_id)
                if hasattr(self, "inline") and self.inline.init_complete:
                    await self.inline._bot.send_message(
                        (await self.client.get_me()).id,
                        self.strings("banned_log").format(
                            peer.id,
                            utils.escape_html(peer.first_name),
                            format_(contact),
                            format_(started_by_you),
                            format_(active_peer),
                            format_(self.get("spam", False)),
                            format_(self.get("delete", False)),
                            format_(True),
                            utils.escape_html(message.raw_text[:3000]),
                        ),
                        parse_mode="HTML",
                        disable_web_page_preview=True,
                    )
            except ValueError:
                pass

        await self.client(BlockRequest(id=cid))

        if self.get("spam", False):
            await self.client(ReportSpamRequest(peer=cid))

        if self.get("delete", False):
            await self.client(DeleteHistoryRequest(peer=cid, just_clear=True, max_id=0))

        self._approve(cid, "banned")

        logger.warning(f"Intruder punished: {cid}")
