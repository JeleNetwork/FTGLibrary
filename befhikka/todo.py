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

# meta pic: https://img.icons8.com/fluency/48/000000/todo-list.png
# meta developer: @hikariatama

from .. import loader, utils
import asyncio
from random import randint
from telethon.tl.types import Message


@loader.tds
class TodoMod(loader.Module):
    """ToDo List"""

    strings = {
        "name": "ToDo",
        "task_removed": "<b>✅ Task removed</b>",
        "task_not_found": "<b>🚫 Task not found</b",
        "new_task": "<b>Task </b><code>#{}</code>:\n<pre>{}</pre>\n{}",
    }

    async def client_ready(self, client, db):
        self.db = db
        self.todolist = self.db.get("ToDo", "todo", {})

        self.imp_levels = [
            "🌌 Watchlist",
            "💻 Proging",
            "⌚️ Work",
            "🎒 Family",
            "🚫 Private",
        ]

    async def tdcmd(self, message: Message) -> None:
        """<importance:int> <item> - Добавить задачу в todo"""

        args = utils.get_args_raw(message)
        try:
            importance = int(args.split()[0])
            task = args.split(" ", 1)[1]
        except Exception:
            importance = 0
            task = args

        try:
            importance = int(task) if task != "" else 0
            reply = await message.get_reply_message()
            if reply:
                task = reply.text
        except Exception:
            pass

        if importance >= len(self.imp_levels):
            importance = 0

        random_id = str(randint(10000, 99999))

        self.todolist[random_id] = [task, importance]

        self.db.set("ToDo", "todo", self.todolist)
        await utils.answer(
            message,
            self.strings("new_task", message).format(
                random_id, str(task), self.imp_levels[importance]
            ),
        )

    async def tdlcmd(self, message: Message) -> None:
        """Показать активные задачи"""
        res = "<b>#ToDo:</b>\n"
        items = {len(self.imp_levels) - i - 1: [] for i in range(len(self.imp_levels))}
        for item_id, item in self.todolist.items():
            items[item[1]].append(
                f" <code>.utd {item_id}</code>: <code>{item[0]}</code>"
            )

        for importance, strings in items.items():
            if len(strings) == 0:
                continue
            res += "\n -{ " + self.imp_levels[importance][2:] + " }-\n"
            res += (
                self.imp_levels[importance][0]
                + ("\n" + self.imp_levels[importance][0]).join(strings)
                + "\n"
            )

        await utils.answer(message, res)

    async def utdcmd(self, message: Message) -> None:
        """<id> - Удалить задачу из todo"""
        args = utils.get_args_raw(message)
        if args.startswith("#"):
            args = args[1:]

        if args not in self.todolist:
            await utils.answer(message, self.strings("task_not_found", message))
            await asyncio.sleep(2)
            await message.delete()
            return

        del self.todolist[args]
        self.db.set("ToDo", "todo", self.todolist)
        await utils.answer(message, self.strings("task_removed", message))
        await asyncio.sleep(2)
        await message.delete()
