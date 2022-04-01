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

# meta pic: https://img.icons8.com/color-glass/50/000000/txt.png
# meta developer: @hikariatama

from .. import loader, utils
from telethon.tl.types import Message
import logging

logger = logging.getLogger(__name__)

mapping = {
    "a": """
█▀▀█
█▄▄█
▀  ▀""",
    "b": """
█▀▀▄
█▀▀▄
▀▀▀""",
    "c": """
█▀▀
█
▀▀▀""",
    "d": """
█▀▀▄
█  █
▀▀▀""",
    "e": """
█▀▀
█▀▀
▀▀▀""",
    "f": """
█▀▀
█▀▀
▀""",
    "g": """
█▀▀▀
█ ▀█
▀▀▀▀""",
    "h": """
█  █
█▀▀█
▀  ▀""",
    "i": """
 ▀
▀█▀
▀▀▀""",
    "j": """
▀
█
█▄█""",
    "k": """
█ █
█▀▄
▀ ▀""",
    "l": """
█
█
▀▀▀""",
    "m": """
█▀▄▀█
█ ▀ █
▀   ▀""",
    "n": """
█▀▀▄
█  █
▀  ▀""",
    "o": """
█▀▀█
█  █
▀▀▀▀""",
    "p": """
█▀▀█
█  █
█▀▀▀""",
    "q": """
█▀▀█
█  █
▀▀█▄""",
    "r": """
█▀▀█
█▄▄▀
█  █""",
    "s": """
█▀▀▀█
▀▀▀▄▄
█▄▄▄█""",
    "t": """
▀▀█▀▀
  █
  █""",
    "u": """
█  █
█  █
▀▄▄▀""",
    "v": """
█   █
 █ █
 ▀▄▀""",
    "w": """
█   █
█ █ █
█▄▀▄█""",
    "x": """
▀▄ ▄▀
  █
▄▀ ▀▄""",
    "y": """
█   █
█▄▄▄█
    █""",
    "z": """
█▀▀▀█
▄▄▄▀▀
█▄▄▄█""",
    " ": """
     

     """,
}


def chunks(lst: list, n: int) -> list:
    return [lst[i : i + n] for i in range(0, len(lst), n)]


def process(cir, text):
    result = ""
    for chunk in chunks(
        [mapping.get(letter.lower(), "").splitlines() for letter in text], cir
    ):
        row = ["" for _ in range(max(list(map(len, mapping.values()))))]
        row_result = []
        for i, line in enumerate(row):
            for letter in chunk:
                try:
                    l_ = letter[i]
                    if len(l_) < 5:
                        l_ += " " * (5 - len(l_))
                    line += f"{l_} "
                except IndexError:
                    pass
            row_result += [line]

        result += "\n".join([r for r in row_result if r.strip()]) + "\n"

    return result.replace(" ", " ")


@loader.tds
class BigTextMod(loader.Module):
    """Creates big ASCII Text"""

    strings = {"name": "BigText"}

    async def btcmd(self, message: Message) -> None:
        """[chars in line] - Create big text"""
        args = utils.get_args_raw(message)
        cir = 6
        if args.split() and args.split()[0].isdigit():
            cir = int(args.split()[0])
            args = args[args.find(" ") + 1 :]

        await utils.answer(message, f"<code>{process(cir, args)}</code>")
