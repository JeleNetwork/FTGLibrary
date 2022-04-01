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

# meta pic: https://img.icons8.com/fluency/50/000000/v-live.png
# meta developer: @hikariatama

from .. import loader
from telethon.tl.types import Message


@loader.tds
class NoMetaMod(loader.Module):
    """Warns people about Meta messages"""

    strings = {
        "name": "NoMeta",
        "no_meta": "<b>👾 <u>Please!</u></b>\n<b>NoMeta</b> aka <i>'Hello', 'Hi' etc.</i>\nAsk <b>directly</b>, what do you want from me.",
        "no_meta_ru": "<b>👾 <u>Пожалуйста!</u></b>\n<b>Не нужно лишних сообщений</b> по типу <i>'Привет', 'Хай' и др.</i>\nСпрашивай(-те) <b>конкретно</b>, что от меня нужно.",
    }

    async def client_ready(self, client, db):
        self.client = client

    @loader.unrestricted
    async def nometacmd(self, message: Message) -> None:
        """Если кто-то отправил мету по типу 'Привет', эта команда его вразумит"""
        await self.client.send_message(
            message.peer_id,
            self.strings("no_meta"),
            reply_to=getattr(message, "reply_to_msg_id", None),
        )
        await message.delete()

    async def watcher(self, message: Message) -> None:
        if not getattr(message, "raw_text", False):
            return

        if not message.is_private:
            return

        meta = ["hi", "hello", "hey there", "konichiwa", "hey"]

        meta_ru = [
            "привет",
            "хай",
            "хелло",
            "хеллоу",
            "хэллоу",
            "коничива",
            "алоха",
            "слушай",
            "о",
            "слуш",
            "м?",
            "а?",
            "хей",
            "хэй",
            "йо",
            "йоу",
            "прив",
            "дан",
            "yo",
            "ку",
        ]

        if message.raw_text.lower() in meta:
            await self.client.send_message(
                message.peer_id, self.strings("no_meta"), reply_to=message.id
            )
            await self.client.send_read_acknowledge(
                message.chat_id, clear_mentions=True
            )

        if message.raw_text.lower() in meta_ru:
            await self.client.send_message(
                message.peer_id, self.strings("no_meta_ru"), reply_to=message.id
            )
            await self.client.send_read_acknowledge(
                message.chat_id, clear_mentions=True
            )
