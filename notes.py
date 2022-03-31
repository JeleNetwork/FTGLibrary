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

# meta pic: https://img.icons8.com/external-justicon-flat-justicon/64/000000/external-note-education-justicon-flat-justicon.png
# meta developer: @hikariatama

from .. import loader, utils  # noqa
from telethon.tl.types import Message  # noqa
import logging

logger = logging.getLogger(__name__)


@loader.tds
class NotesMod(loader.Module):
    """Advanced notes module with folders and other features"""

    strings = {
        "name": "Notes",
        "saved": "💾 <b>Saved note with name </b><code>{}</code>.\nFolder: </b><code>{}</code>.</b>",
        "no_reply": "🚫 <b>Reply and note name are required.</b>",
        "no_name": "🚫 <b>Specify note name.</b>",
        "no_note": "🚫 <b>Note not found.</b>",
        "available_notes": "💾 <b>Current notes:</b>\n",
        "no_notes": "😔 <b>You have no notes yet</b>",
        "deleted": "🙂 <b>Deleted note </b><code>{}</code>",
    }

    def get(self, *args) -> dict:
        return self.db.get(self.strings["name"], *args)

    def set(self, *args) -> None:
        return self.db.set(self.strings["name"], *args)

    async def client_ready(self, client, db) -> None:
        self.db = db
        self.client = client
        self._notes = self.get("notes", {})

    async def hsavecmd(self, message: Message) -> None:
        """[folder] <name> - Save new note"""
        args = utils.get_args_raw(message)

        if len(args.split()) >= 2:
            folder = args.split()[0]
            args = args.split(maxsplit=1)[1]
        else:
            folder = "global"

        reply = await message.get_reply_message()

        if not (reply and args):
            await utils.answer(message, self.strings("no_reply"))
            return

        if folder not in self._notes:
            self._notes[folder] = {}
            logger.warning(f"Created new folder {folder}")

        asset = await self.db.store_asset(reply)

        if getattr(reply, "video", False):
            type_ = "🎞"
        elif getattr(reply, "photo", False):
            type_ = "🖼"
        elif getattr(reply, "voice", False):
            type_ = "🗣"
        elif getattr(reply, "audio", False):
            type_ = "🎧"
        elif getattr(reply, "file", False):
            type_ = "📝"
        else:
            type_ = "🔹"

        self._notes[folder][args] = {"id": asset, "type": type_}

        self.set("notes", self._notes)

        await utils.answer(message, self.strings("saved").format(args, folder))

    def _get_note(self, name):
        for category, notes in self._notes.items():
            for note, asset in notes.items():
                if note == name:
                    return asset

    def _del_note(self, name):
        for category, notes in self._notes.copy().items():
            for note, asset in notes.copy().items():
                if note == name:
                    del self._notes[category][note]

                    if not self._notes[category]:
                        del self._notes[category]

                    self.set("notes", self._notes)
                    return True

        return False

    async def hgetcmd(self, message: Message) -> None:
        """<name> - Show specified note"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("no_name"))
            return

        asset = self._get_note(args)
        if not asset:
            await utils.answer(message, self.strings("no_note"))
            return

        await self.client.send_message(
            message.peer_id,
            await self.db.fetch_asset(asset["id"]),
            reply_to=getattr(message, "reply_to_msg_id", False),
        )

        if message.out:
            await message.delete()

    async def hdelcmd(self, message: Message) -> None:
        """<name> - Delete specified note"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("no_name"))
            return

        asset = self._get_note(args)
        if not asset:
            await utils.answer(message, self.strings("no_note"))
            return

        try:
            await (await self.db.fetch_asset(asset["id"])).delete()
        except Exception:
            pass

        self._del_note(args)

        await utils.answer(message, self.strings("deleted").format(args))

    async def hlistcmd(self, message: Message) -> None:
        """[folder] - List all notes"""
        args = utils.get_args_raw(message)

        if not self._notes:
            await utils.answer(message, self.strings("no_notes"))
            return

        result = self.strings("available_notes")

        if not args or args not in self._notes:
            for category, notes in self._notes.items():
                result += f"\n🔸 <b>{category}</b>\n"
                for note, asset in notes.items():
                    result += f"    {asset['type']} <code>{note}</code>\n"

            await utils.answer(message, result)
            return

        for note, asset in self._notes[args].items():
            result += f"{asset['type']} <code>{note}</code>\n"

        await utils.answer(message, result)
