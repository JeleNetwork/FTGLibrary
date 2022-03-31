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

# meta pic: https://img.icons8.com/stickers/100/000000/python.png
# meta developer: @hikariatama

from .. import loader, utils
from telethon.tl.types import Message
import logging
import requests
import os
import re
import io
from random import choice

logger = logging.getLogger(__name__)

CMD = (
    'black --exclude "/(\\.direnv|\\.eggs|\\.git'
    "|\\.h g|\\.mypy_cache|\\.nox|\\.tox|\\.venv|"
    "venv|\\.svn |_build|buck-out|build|dist|"
    '__pycache__)/" '
    "-l 10000 -t py39 linter_tmp.py"
)

URL = r"(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+"

captions = [
    "Here is your new fresh linted code! Enjoy",
    "This was such a hard work to clean this code... Uff..",
    "Here we go!",
    "Glad to be your virtual code-cleaning-maid!",
    "Take this, master!",
]

faces = [
    "ʕ•ᴥ•ʔ",
    "(ᵔᴥᵔ)",
    "(◕‿◕✿)",
    "(づ￣ ³￣)づ",
    "♥‿♥",
    "~(˘▾˘~)",
    "(｡◕‿◕｡)",
    "｡◕‿◕｡",
    "ಠ‿↼",
]


@loader.tds
class PyLinterMod(loader.Module):
    """`Black` plugin wrapper for telegram"""

    strings = {"name": "PyLinter", "no_code": "🚫 <b>Please, specify code to lint</b>"}

    def get(self, *args) -> dict:
        return self.db.get(self.strings["name"], *args)

    def set(self, *args) -> None:
        return self.db.set(self.strings["name"], *args)

    async def client_ready(self, client, db) -> None:
        self.db = db
        self.client = client

    async def lintcmd(self, message: Message) -> None:
        """[code|reply] - Perform automatic lint to python code"""
        reply = await message.get_reply_message()
        args = utils.get_args_raw(message)
        media = message.media or (reply.media if reply else False)

        if media:
            try:
                args = (await self.client.download_file(media)).decode("utf-8")
            except TypeError:
                pass

        if not args:
            if not reply:
                await utils.answer(message, self.strings("no_code"))
                return

            args = reply.raw_text

        if re.match(URL, args):
            args = (await utils.run_sync(requests.get, args)).text

        with open("linter_tmp.py", "w") as f:
            f.write(args)

        os.popen(CMD).read()

        with open("linter_tmp.py", "r") as f:
            lint_result = f.read()

        os.remove("linter_tmp.py")

        if len(lint_result) < 2048:
            await utils.answer(
                message, f"<code>{utils.escape_html(lint_result)}</code>"
            )
            return

        file = io.BytesIO(args.encode("utf-8"))
        file.name = "lint_result.py"
        await self.client.send_file(
            message.peer_id,
            file,
            caption=f"<i>{choice(captions)}</i> <b>{choice(faces)}</b>",
        )
        if message.out:
            await message.delete()
