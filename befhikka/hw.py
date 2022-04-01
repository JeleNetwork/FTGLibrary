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

# meta pic: https://img.icons8.com/fluency/48/000000/khan-academy.png
# meta developer: @hikariatama

from .. import loader, utils
import asyncio
from random import randint
from telethon.tl.types import Message


@loader.tds
class HomeworkMod(loader.Module):
    """Simple Homework planner"""

    strings = {
        "name": "HomeWork",
        "no_hometask": "<b>You haven't provided hometask</b>",
        "new_hometask": "<b>Hometask </b><code>#{}</code>:\n<pre>{}</pre>",
        "not_found": "<b>🚫 Hometask not found</b",
        "removed": "<b>✅ Hometask removed</b>",
    }

    async def client_ready(self, client, db) -> None:
        self.db = db
        self.hw = self.db.get("HomeWork", "hw", {})

    async def hwcmd(self, message: Message) -> None:
        """<item> - New hometask"""

        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if args == "" and not reply:
            await utils.answer(message, self.strings("no_hometask"))
            await asyncio.sleep(2)
            await message.delete()
            return

        if args == "":
            args = reply.text

        random_id = str(randint(10000, 99999))

        self.hw[random_id] = args

        self.db.set("HomeWork", "hw", self.hw)
        await utils.answer(
            message, self.strings("new_hometask", message).format(random_id, str(args))
        )

    @loader.unrestricted
    async def hwlcmd(self, message: Message) -> None:
        """List of hometasks"""
        res = "<b>#HW:</b>\n\n"
        for item_id, item in self.hw.items():
            res += f"🔸 <code>.uhw {item_id}</code>: <code>{item}" + "</code>\n"
        await utils.answer(message, res)

    async def uhwcmd(self, message: Message) -> None:
        """<id> - Remove hometask"""
        args = utils.get_args_raw(message)
        if args.startswith("#"):
            args = args[1:]

        if args not in self.hw:
            await utils.answer(message, self.strings("not_found", message))
            await asyncio.sleep(2)
            await message.delete()
            return

        del self.hw[args]
        self.db.set("HomeWork", "hw", self.hw)
        await utils.answer(message, self.strings("removed", message))
        await asyncio.sleep(2)
        await message.delete()
