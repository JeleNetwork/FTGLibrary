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

# meta pic: https://img.icons8.com/fluency/48/000000/angry.png
# meta developer: @hikariatama

from .. import loader, utils
import random

from telethon.tl.types import Message


@loader.tds
class PoliteInsultMod(loader.Module):
    """If you need to insult but to be intelligent"""

    strings = {"name": "PoliteInsult"}

    async def insultocmd(self, message: Message) -> None:
        """Use when angry"""
        adjectives_start = [
            "вспыльчивый(-ая)",
            "невоспитанный(-ая)",
            "осточертевший(-ая) мне",
            "глуповатый(-ая)",
            "надменный(-ая)",
            "неиндивидуалистичный(-ая)",
            "неиндифферентный(-ая)",
            "недисциплинированный(-ая)",
        ]
        nouns = ["человек", "участник(-ца) данного чата"]
        starts = [
            "Не хочу делать поспешных выводов, но",
            "Я, конечно, не могу утверждать, и это мое субъективное мнение, но",
            "Проанализировав ситуацию, я могу высказать свое субъективное мнение. Оно заключается в том, что",
            "Не пытаясь никого осокорбить, а лишь высказывая свою скромную точку зрения, которая не влияет на точку зрения других людей, могу сказать, что",
            "Не преследуя попытку затронуть какие-либо социальные меньшинства, хочу сказать, что",
        ]
        ends = ["!!!!", "!", "."]
        start = random.choice(starts)
        adjective_start = random.choice(adjectives_start)
        adjective_mid = random.choice(adjectives_start)
        noun = random.choice(nouns)
        end = random.choice(ends)
        insult = (
            (
                f"{start} ты - {adjective_start} {adjective_mid}"
                + (" " if adjective_mid else "")
            )
            + noun
        ) + end

        await utils.answer(message, insult)
