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

# meta pic: https://img.icons8.com/color/48/000000/anonymous-mask.png
# meta developer: @hikariatama
# scope: inline
# scope: geektg_only

from .. import loader, utils
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InlineKeyboardButton,
    InputTextMessageContent,
)
import logging
from ..inline import GeekInlineQuery, rand
from telethon.utils import get_display_name
import time

logger = logging.getLogger(__name__)


@loader.tds
class GeekSpoilersMod(loader.Module):
    """Create spoilers, that can be accessed only by certain users"""

    strings = {"name": "GeekSpoilers"}

    def get(self, *args) -> dict:
        return self.db.get(self.strings["name"], *args)

    def set(self, *args) -> None:
        return self.db.set(self.strings["name"], *args)

    async def client_ready(self, client, db) -> None:
        self.db = db
        self.client = client
        self._messages = {
            message_id: message
            for message_id, message in self.get("messages", {}).items()
            if message["ttl"] > time.time()
        }

    async def inline__close(self, call: CallbackQuery) -> None:
        await call.delete()

    async def hide_inline_handler(self, query: GeekInlineQuery) -> None:
        """Create new hidden message"""
        text = query.args
        for_user = "Specify username in the end"
        for_user_id = None
        user = None
        if len(text.split()) > 1 and text.split()[-1].startswith("@"):
            try:
                user = await self.client.get_entity(text.split()[-1])
            except Exception:
                pass
            else:
                for_user = "Hidden message for " + get_display_name(user)
                for_user_id = user.id

        markup = None

        if for_user_id:
            message_id = rand(16)
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("👀 Open", callback_data=message_id))

            self._messages[message_id] = {
                "text": " ".join(text.split(" ")[:-1]),
                "ttl": round(time.time() + 12 * 60 * 60),
                "for": for_user_id,
            }

            self.set("messages", self._messages)

        await query.answer(
            [
                InlineQueryResultArticle(
                    id=rand(20),
                    title=for_user,
                    description="ℹ Only (s)he will be able to open it",
                    input_message_content=InputTextMessageContent(
                        f'🙈 <b>Hidden message for <a href="tg://user?id={for_user_id}">{utils.escape_html(get_display_name(user))}</a></b>\n<i>You can open this message only once!</i>'
                        if user
                        else f"🚫 <b>User not specified</b>",
                        "HTML",
                        disable_web_page_preview=True,
                    ),
                    thumb_url="https://img.icons8.com/color/48/000000/anonymous-mask.png",
                    thumb_width=128,
                    thumb_height=128,
                    reply_markup=markup,
                )
            ],
            cache_time=0,
        )

    async def button_callback_handler(self, call: CallbackQuery) -> None:
        """Process button presses
        @allow: all
        """
        if (
            call.data not in self._messages
            or call.from_user.id != self._messages[call.data]["for"]
            and call.from_user.id not in self.client.dispatcher.security._owner
        ):
            return

        await call.answer(self._messages[call.data]["text"], show_alert=True)

        if call.from_user.id not in self.client.dispatcher.security._owner:
            del self._messages[call.data]
            await call.delete()
