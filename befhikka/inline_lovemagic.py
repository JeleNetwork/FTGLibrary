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

# meta pic: https://img.icons8.com/stickers/100/000000/like.png
# meta developer: @hikariatama
# scope: inline
# scope: geektg_only

import random
from .. import utils, loader
from asyncio import sleep
from telethon.tl.types import Message
from aiogram.types import CallbackQuery


@loader.tds
class ILYMod(loader.Module):
    """Famous TikTok hearts animation implemented in GeekTG w/o logspam"""

    strings = {
        "name": "LoveMagicInline",
        "message": "<b>❤️‍🔥 I want to tell you something...</b>\n<i>{}</i>",
    }

    async def inline__handler(self, call: CallbackQuery, text: str) -> None:
        arr = ["❤️", "🧡", "💛", "💚", "💙", "💜", "🤎", "🖤", "💖"]
        h = "🤍"
        for i in arr:
            await call.edit(
                "".join(
                    [
                        h * 9,
                        "\n",
                        h * 2,
                        i * 2,
                        h,
                        i * 2,
                        h * 2,
                        "\n",
                        h,
                        i * 7,
                        h,
                        "\n",
                        h,
                        i * 7,
                        h,
                        "\n",
                        h,
                        i * 7,
                        h,
                        "\n",
                        h * 2,
                        i * 5,
                        h * 2,
                        "\n",
                        h * 3,
                        i * 3,
                        h * 3,
                        "\n",
                        h * 4,
                        i,
                        h * 4,
                        "\n",
                        h * 9,
                    ]
                )
            )
            await sleep(0.5)
        for _ in range(8):
            rand = random.choices(arr, k=34)
            await call.edit(
                "".join(
                    [
                        h * 9,
                        "\n",
                        h * 2,
                        rand[0],
                        rand[1],
                        h,
                        rand[2],
                        rand[3],
                        h * 2,
                        "\n",
                        h,
                        rand[4],
                        rand[5],
                        rand[6],
                        rand[7],
                        rand[8],
                        rand[9],
                        rand[10],
                        h,
                        "\n",
                        h,
                        rand[11],
                        rand[12],
                        rand[13],
                        rand[14],
                        rand[15],
                        rand[16],
                        rand[17],
                        h,
                        "\n",
                        h,
                        rand[18],
                        rand[19],
                        rand[20],
                        rand[21],
                        rand[22],
                        rand[23],
                        rand[24],
                        h,
                        "\n",
                        h * 2,
                        rand[25],
                        rand[26],
                        rand[27],
                        rand[28],
                        rand[29],
                        h * 2,
                        "\n",
                        h * 3,
                        rand[30],
                        rand[31],
                        rand[32],
                        h * 3,
                        "\n",
                        h * 4,
                        rand[33],
                        h * 4,
                        "\n",
                        h * 9,
                    ]
                )
            )
            await sleep(0.5)
        fourth = "".join(
            [
                h * 9,
                "\n",
                h * 2,
                arr[0] * 2,
                h,
                arr[0] * 2,
                h * 2,
                "\n",
                h,
                arr[0] * 7,
                h,
                "\n",
                h,
                arr[0] * 7,
                h,
                "\n",
                h,
                arr[0] * 7,
                h,
                "\n",
                h * 2,
                arr[0] * 5,
                h * 2,
                "\n",
                h * 3,
                arr[0] * 3,
                h * 3,
                "\n",
                h * 4,
                arr[0],
                h * 4,
                "\n",
                h * 9,
            ]
        )
        await call.edit(fourth)
        for _ in range(10):
            fourth = fourth.replace("🤍", "❤️‍🔥", 4)
            await call.edit(fourth)
            await sleep(0.3)
        for i in range(8):
            await call.edit((arr[0] * (8 - i) + "\n") * (8 - i))
            await sleep(0.5)
        for i in [" ".join(text.split()[: i + 1]) for i in range(len(text.split()))]:
            await call.edit(f"<b>{i}</b>")
            await sleep(0.5)

        await sleep(10)
        await call.edit(
            f"<b>{text}</b>",
            reply_markup=[[{"text": "💔 Хочу также!", "url": "https://t.me/chat_ftg"}]],
        )

        await call.unload()

    async def inline__handler_gay(self, call: CallbackQuery, text):
        heart_template = """🤍🤍🧡🧡🤍🤍🤍🧡🧡🤍🤍
🤍🧡🧡🧡🧡🤍🧡🧡🧡🧡🤍
🧡🧡🧡🧡🧡🧡🧡🧡🧡🧡🧡
🧡🧡🧡🧡🧡🧡🧡🧡🧡🧡🧡
🧡🧡🧡🧡🧡🧡🧡🧡🧡🧡🧡
🤍🧡🧡🧡🧡🧡🧡🧡🧡🧡🤍
🤍🤍🧡🧡🧡🧡🧡🧡🧡🤍🤍
🤍🤍🤍🧡🧡🧡🧡🧡🤍🤍🤍
🤍🤍🤍🤍🧡🧡🧡🤍🤍🤍🤍
🤍🤍🤍🤍🤍🧡🤍🤍🤍🤍🤍""".splitlines()
        hearts = ["❤️", "🧡", "💛", "💚", "💙", "💜"]
        offset = 0

        for _ in range(16):
            await call.edit(
                "\n".join(
                    [
                        "<code>"
                        + line.replace(
                            "🧡", hearts[(i + offset) % (len(hearts) - 1)], 13
                        )
                        + "</code>"
                        for i, line in enumerate(heart_template)
                    ]
                )
            )
            await sleep(0.5)
            offset += 1

        for i in [" ".join(text.split()[: i + 1]) for i in range(len(text.split()))]:
            await call.edit(f"<b>{i}</b>")
            await sleep(0.5)

        await sleep(10)
        await call.edit(
            f"<b>{text}</b>",
            reply_markup=[[{"text": "💔 Хочу также!", "url": "https://t.me/chat_ftg"}]],
        )

        await call.unload()

    async def ilycmd(self, message: Message) -> None:
        """Send inline message with animating hearts"""
        args = utils.get_args_raw(message)
        await self.inline.form(
            self.strings("message").format("*" * (len(args) or 9)),
            reply_markup=[
                [
                    {
                        "text": "🧸 Open",
                        "callback": self.inline__handler,
                        "args": (args or "I ❤️ you!",),
                    }
                ]
            ],
            force_me=False,
            message=message,
            ttl=60 * 60,
        )

    async def ilymatecmd(self, message: Message) -> None:
        """Send inline message with animating hearts v2"""
        args = utils.get_args_raw(message)
        await self.inline.form(
            self.strings("message").format("*" * (len(args) or 21)),
            reply_markup=[
                [
                    {
                        "text": "🧸 Open",
                        "callback": self.inline__handler_gay,
                        "args": (args or "I am gay and I 💙 you!",),
                    }
                ]
            ],
            force_me=False,
            message=message,
            ttl=60 * 60,
        )
