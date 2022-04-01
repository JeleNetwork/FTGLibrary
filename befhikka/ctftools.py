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

# meta pic: https://img.icons8.com/fluency/48/000000/password1.png
# meta developer: @hikariatama

from .. import loader, utils
import os
import time
import io
from telethon.tl.types import Message


@loader.tds
class CTFToolsMod(loader.Module):
    """Basic CTF Toolkit"""

    strings = {
        "name": "CTF Toolkit",
        "processing": "<b>📤 Processing...</b>",
        "file_not_specified": "<b>What should I read?... 🗿</b>",
        "read_error": "<b>🗿 File read error</b>",
    }

    async def filetypecmd(self, message: Message) -> None:
        """Linux File command wrapper"""
        reply = await message.get_reply_message()
        message = await utils.answer(message, self.strings("processing", message))
        if not reply and type(message.media) is None:
            await utils.answer(message, self.strings("file_not_specified", message))
            return
        if not reply:
            media = message.media
            print(media)
        else:
            media = reply.media

        filename = f"/tmp/{str(round(time.time()))}.scan"

        file = await message.client.download_file(media)
        try:
            open(filename, "wb").write(file)

            res = str(os.popen(f"file {filename}").read()).replace(filename + ": ", "")
            os.system(f"rm -rf {filename}")

            await utils.answer(message, f"<code>{res}</code>")
        except Exception:
            await utils.answer(message, self.strings("read_error", message))

    async def stringscmd(self, message: Message) -> None:
        """Linux Strings | grep . command wrapper"""
        await utils.answer(message, self.strings("processing", message))
        args = utils.get_args_raw(message)
        grep = "" if args == "" else f" | grep {args}"
        reply = await message.get_reply_message()
        if not reply and type(message.media) is None:
            await utils.answer(message, self.strings("file_not_specified", message))
            return
        if not reply:
            media = message.media
            print(media)
        else:
            media = reply.media

        filename = f"/tmp/{str(round(time.time()))}"

        file = await message.client.download_file(media)
        try:
            open(filename, "wb").write(file)

            res = str(os.popen(f"strings {filename}{grep}").read())
            os.system(f"rm -rf {filename}")
            try:
                await utils.answer(message, f"<code>{res}</code>")
            except Exception:
                txt = io.BytesIO(res.encode("utf-8"))
                txt.name = "strings_result.txt"
                await message.delete()
                await message.client.send_file(message.to_id, txt)
        except Exception:
            await utils.answer(message, self.strings("read_error", message))
