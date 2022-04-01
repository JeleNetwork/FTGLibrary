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

# meta pic: https://img.icons8.com/fluency/48/000000/radio-waves.png
# meta developer: @hikariatama

from .. import loader, utils
import asyncio
from telethon.tl.types import Message


@loader.tds
class FuckTagsMod(loader.Module):
    """Auto-read tags and messages in selected chats"""

    strings = {
        "name": "FuckTags",
        "args": "🦊 <b>Incorrect args specified</b>",
        "on": "🦊 <b>Now I ignore tags in this chat</b>",
        "off": "🦊 <b>Now I don't ignore tags in this chat</b>",
        "on_strict": "🦊 <b>Now I automatically read messages in this chat</b>",
        "off_strict": "🦊 <b>Now I don't automatically read messages in this chat</b>",
        "do_not_tag_me": "🦊 <b>Please, do not tag me.</b>",
    }

    async def client_ready(self, client, db):
        self.db = db
        self.client = client
        self._ratelimit = []

    async def fucktagscmd(self, message: Message) -> None:
        """<chat|optional> - Toggle notags"""
        args = utils.get_args_raw(message)
        try:
            try:
                args = int(args)
            except Exception:
                pass
            cid = (await self.client.get_entity(args)).id
        except Exception:
            cid = utils.get_chat_id(message)

        self._ratelimit = list(set(self._ratelimit) - set([cid]))

        if cid not in self.db.get("FuckTags", "tags", []):
            self.db.set("FuckTags", "tags", self.db.get("FuckTags", "tags", []) + [cid])
            await utils.answer(message, self.strings("on", message))
        else:
            self.db.set(
                "FuckTags",
                "tags",
                list(set(self.db.get("FuckTags", "tags", [])) - set([cid])),
            )
            await utils.answer(message, self.strings("off", message))

    async def fuckallcmd(self, message: Message) -> None:
        """<chat|optional> - Toggle autoread"""
        args = utils.get_args_raw(message)
        try:
            if str(args).isdigit():
                args = int(args)
            cid = (await self.client.get_entity(args)).id
        except Exception:
            cid = utils.get_chat_id(message)

        if cid not in self.db.get("FuckTags", "strict", []):
            self.db.set(
                "FuckTags", "strict", self.db.get("FuckTags", "strict", []) + [cid]
            )
            await utils.answer(message, self.strings("on_strict", message))
        else:
            self.db.set(
                "FuckTags",
                "strict",
                list(set(self.db.get("FuckTags", "strict", [])) - set([cid])),
            )
            await utils.answer(message, self.strings("off_strict", message))

    async def fuckchatscmd(self, message: Message) -> None:
        """Показать активные авточтения в чатах"""
        res = "<b>== FuckTags ==</b>\n"
        for chat in self.db.get("FuckTags", "tags", []):
            try:
                c = await self.client.get_entity(chat)
                res += (c.title if c.title is not None else c.first_name) + "\n"
            except Exception:
                res += str(chat) + "\n"

        res += "\n<b>== FuckMessages ==</b>\n"
        for chat in self.db.get("FuckTags", "strict", []):
            try:
                c = await self.client.get_entity(chat)
                res += (c.title if c.title is not None else c.first_name) + "\n"
            except Exception:
                res += str(chat) + "\n"

        await utils.answer(message, res)

    async def watcher(self, message: Message) -> None:
        try:
            if (
                utils.get_chat_id(message) in self.db.get("FuckTags", "tags", [])
                and message.mentioned
            ):
                await self.client.send_read_acknowledge(
                    message.chat_id, message, clear_mentions=True
                )
                if utils.get_chat_id(message) not in self._ratelimit:
                    msg = await utils.answer(
                        message, self.strings("do_not_tag_me", message)
                    )
                    self._ratelimit.append(utils.get_chat_id(message))
                    await asyncio.sleep(3)
                    try:
                        msg = msg[0]
                    except Exception:
                        pass

                    await msg.delete()
            elif utils.get_chat_id(message) in self.db.get("FuckTags", "strict", []):
                await self.client.send_read_acknowledge(message.chat_id, message)
        except Exception:
            pass
