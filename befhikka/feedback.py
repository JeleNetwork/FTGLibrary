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

# meta pic: https://img.icons8.com/external-wanicon-lineal-color-wanicon/64/000000/external-feedback-influencer-marketing-wanicon-lineal-color-wanicon.png
# meta developer: @hikariatama
# scope: inline
# scope: geektg_min 3.1.16
# scope: geektg_only

import abc
from .. import loader, utils
import logging
import time
from telethon.utils import get_display_name

from aiogram.types import Message as AiogramMessage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

logger = logging.getLogger(__name__)


@loader.tds
class FeedbackMod(loader.Module):
    """Simple feedback bot for GeekTG"""

    __metaclass__ = abc.ABCMeta

    strings = {
        "name": "Feedback",
        "/start": "🤵‍♀️ <b>Hello. I'm feedback bot of {}. Read /nometa before continuing</b>\n<b>You can send only one message per minute</b>",
        "/nometa": (
            "👨‍🎓 <b><u>Internet-talk rules:</u></b>\n\n"
            "<b>🚫 Do <u>not</u> send just 'Hello'</b>\n"
            "<b>🚫 Do <u>not</u> advertise</b>\n"
            "<b>🚫 Do <u>not</u> insult</b>\n"
            "<b>🚫 Do <u>not</u> split message</b>\n"
            "<b>✅ Write your question in one message</b>"
        ),
        "enter_message": "✍️ <b>Enter your message here</b>",
        "sent": "✅ <b>Your message has been sent to owner</b>",
    }

    def get(self, *args) -> dict:
        return self._db.get(self.strings["name"], *args)

    def set(self, *args) -> None:
        return self._db.set(self.strings["name"], *args)

    async def client_ready(self, client, db) -> None:
        self._db = db
        self._client = client
        self._me = (await client.get_me()).id
        self._name = utils.escape_html(get_display_name(await client.get_me()))

        if not hasattr(self, "inline"):
            raise Exception("GeekTG Only")

        self._bot = self.inline._bot
        self._ratelimit = {}
        self._markup = InlineKeyboardMarkup()
        self._markup.add(
            InlineKeyboardButton(
                "✍️ Leave a message [1 per minute]", callback_data="fb_leave_message"
            )
        )

        self._cancel = InlineKeyboardMarkup()
        self._cancel.add(InlineKeyboardButton("🚫 Cancel", callback_data="fb_cancel"))

        self.__doc__ = (
            "Feedback bot\n"
            f"Your feeback link: t.me/{self.inline._bot_username}?start=feedback\n"
            "You can freely share it"
        )

    async def aiogram_watcher(self, message: AiogramMessage) -> None:
        if message.text == "/start feedback":
            await message.answer(
                self.strings("/start").format(self._name), reply_markup=self._markup
            )
        elif message.text == "/nometa":
            await message.answer(self.strings("/nometa"), reply_markup=self._markup)
        elif self.inline.gs(message.from_user.id) == "fb_send_message":
            await self._bot.forward_message(
                self._me, message.chat.id, message.message_id
            )
            await message.answer(self.strings("sent"))
            self._ratelimit[message.from_user.id] = time.time() + 60
            self.inline.ss(message.from_user.id, False)

    async def feedback_callback_handler(self, call: CallbackQuery) -> None:
        """
        Handles button clicks
        @allow: all
        """
        if call.data == "fb_cancel":
            self.inline.ss(call.from_user.id, False)
            await self._bot.delete_message(
                call.message.chat.id, call.message.message_id
            )
            return

        if call.data != "fb_leave_message":
            return

        if (
            call.from_user.id in self._ratelimit
            and self._ratelimit[call.from_user.id] > time.time()
        ):
            await call.answer(
                f"You can send next message in {self._ratelimit[call.from_user.id] - time.time():.0f} second(-s)",
                show_alert=True,
            )
            return

        self.inline.ss(call.from_user.id, "fb_send_message")
        await self._bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=self.strings("enter_message"),
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=self._cancel,
        )
