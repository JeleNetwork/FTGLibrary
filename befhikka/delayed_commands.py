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

# meta pic: https://img.icons8.com/fluency/48/000000/schedule-mail.png
# meta developer: @hikariatama

from .. import loader, utils
import asyncio
import re
from telethon.tl.types import Message


@loader.tds
class DelayedMod(loader.Module):
    """Delay command execution or remove its output after delay"""

    strings = {
        "name": "DelayedCommands",
        "no_such_command": "<b>No such command</b>",
    }

    async def client_ready(self, client, db):
        self.db = db
        self.client = client

    @staticmethod
    def s2time(temp_time: str) -> int:
        seconds, minutes, hours, days, weeks, months = 0, 0, 0, 0, 0, 0

        try:
            seconds = int(str(re.search("([0-9]+)s", temp_time).group(1)))
        except Exception:
            pass

        try:
            minutes = int(str(re.search("([0-9]+)min", temp_time).group(1))) * 60
        except Exception:
            pass

        try:
            hours = int(str(re.search("([0-9]+)h", temp_time).group(1))) * 60 * 60
        except Exception:
            pass

        try:
            days = int(str(re.search("([0-9]+)d", temp_time).group(1))) * 60 * 60 * 24
        except Exception:
            pass

        try:
            weeks = (
                int(str(re.search("([0-9]+)w", temp_time).group(1))) * 60 * 60 * 24 * 7
            )
        except Exception:
            pass

        try:
            months = (
                int(str(re.search("([0-9]+)m[^i]", temp_time).group(1)))
                * 60
                * 60
                * 24
                * 31
            )
        except Exception:
            pass

        return round(seconds + minutes + hours + days + weeks + months)

    async def dcmd(self, message: Message) -> None:
        """<time (1d 2min etc)> <cmd> - Delay command for specified time. Resets when module or ub are restarted"""
        args = utils.get_args_raw(message)

        command = args.split(" ", 1)[1]
        if command.startswith("."):
            command = command[1:]

        if command.split()[0] not in self.allmodules.commands:
            await utils.answer(message, self.strings("no_such_command", message))
            await asyncio.sleep(3)
            await message.delete()
            return

        # print(args.split())

        reply = await message.get_reply_message()

        await message.delete()
        await asyncio.sleep(self.s2time(args.split()[0]))
        # await message.client.send_message('me', '.help')
        await self.allmodules.commands[command.split()[0]](
            await message.client.send_message(
                utils.get_chat_id(message), f".{command}", reply_to=reply
            )
        )

    async def adcmd(self, message: Message) -> None:
        """<time (1d 2min etc)> <cmd> - Execute command, and delete output after some time. WORKS NOT WITH ALL MODULES"""
        args = utils.get_args_raw(message)

        command = args.split(" ", 1)[1]
        if command.startswith("."):
            command = command[1:]

        if command.split()[0] not in self.allmodules.commands:
            await utils.answer(message, self.strings("no_such_command", message))
            await asyncio.sleep(3)
            await message.delete()
            return

        reply = await message.get_reply_message()

        await message.delete()
        msg = await message.client.send_message(
            utils.get_chat_id(message), f".{command}", reply_to=reply
        )

        await self.allmodules.commands[command.split()[0]](msg)
        delay = self.s2time(args.split()[0])
        await asyncio.sleep(delay)
        await msg.delete()
