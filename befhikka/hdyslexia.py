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

# meta pic: https://img.icons8.com/fluency/48/000000/quote-right.png
# meta developer: @hikariatama

from .. import loader, utils
from random import shuffle
import re
from telethon.tl.types import Message


@loader.tds
class DyslexiaMod(loader.Module):
    """Shows the text as how you would see it if you have dyslexia"""

    strings = {"name": "Dyslexia", "no_text": "🎈 <b>You need to provide text</b>"}

    @loader.unrestricted
    async def dyslexcmd(self, message: Message) -> None:
        """<text | reply> - Show, how people with dyslexia would have seen this text"""
        args = utils.get_args_raw(message)
        if not args:
            try:
                args = (await message.get_reply_message()).text
            except Exception:
                return await utils.answer(message, self.strings("no_text"))

        res = ""
        for word in args.split():
            newline = False
            if "\n" in word:
                word = word.replace("\n", "")
                newline = True

            to_shuffle = re.sub(r"[^a-zA-Zа-яА-Я]", "", word)[1:-1]
            shuffled = list(to_shuffle)
            shuffle(shuffled)

            res += word.replace(to_shuffle, "".join(shuffled)) + " "
            if newline:
                res += "\n"

        return await utils.answer(message, res)
