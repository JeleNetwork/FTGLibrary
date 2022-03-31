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

# meta pic: https://img.icons8.com/external-wanicon-flat-wanicon/64/000000/external-read-free-time-wanicon-flat-wanicon.png
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
from telethon.tl.types import Message
import time

logger = logging.getLogger(__name__)


@loader.tds
class LongReadMod(loader.Module):
    """Pack longreads under button spoilers"""

    strings = {
        "name": "LongRead",
        "no_text": "🚫 <b>Please, specify text to hide</b>",
        "longread": "🗄 <b>This is long read</b>\n<i>Click button to show text!\nThis button is active withing 6 hours</i>",  # noqa
    }

    def get(self, *args) -> dict:
        return self.db.get(self.strings["name"], *args)

    def set(self, *args) -> None:
        return self.db.set(self.strings["name"], *args)

    async def client_ready(self, client, db) -> None:
        self.db = db
        self.client = client
        self._longreads = {
            id_: obj
            for id_, obj in self.get("longreads", {}).items()
            if obj["ttl"] > time.time()
        }

    async def inline__close(self, call: CallbackQuery) -> None:
        await call.delete()

    def _create_longread(self, text: str) -> InlineKeyboardMarkup:
        message_id = rand(16)

        self._longreads[message_id] = {
            "text": text,
            "ttl": round(time.time() + 6 * 60 * 60),
        }

        self.set("longreads", self._longreads)

        return message_id

    async def lr_inline_handler(self, query: GeekInlineQuery) -> None:
        """Create new hidden message"""
        text = query.args

        if not text:
            return

        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton(
                "📖 Open spoiler", callback_data=self._create_longread(text)
            )
        )

        await query.answer(
            [
                InlineQueryResultArticle(
                    id=rand(20),
                    title="Create new longread",
                    description="ℹ This will create button-spoiler",
                    input_message_content=InputTextMessageContent(
                        self.strings("longread"), "HTML", disable_web_page_preview=True
                    ),
                    thumb_url="https://img.icons8.com/external-wanicon-flat-wanicon/64/000000/external-read-free-time-wanicon-flat-wanicon.png",  # noqa
                    thumb_width=128,
                    thumb_height=128,
                    reply_markup=markup,
                )
            ],
            cache_time=0,
        )

    async def lrcmd(self, message: Message) -> None:
        """<text> - Create new longread"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("no_text"))
            return

        await self.inline.form(
            self.strings("longread"),
            message=message,
            reply_markup=[
                [{"text": "📖 Open spoiler", "data": self._create_longread(args)}]
            ],
        )

    async def button_callback_handler(self, call: CallbackQuery) -> None:
        """Process button presses
        @allow: all
        """
        if call.data not in self._longreads:
            return

        await self.inline._bot.edit_message_text(
            inline_message_id=call.inline_message_id,
            text=self._longreads[call.data]["text"],
            disable_web_page_preview=True,
        )

        await call.answer()

        del self._longreads[call.data]
