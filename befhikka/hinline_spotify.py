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

# meta pic: https://img.icons8.com/cute-clipart/64/000000/playstation-buttons.png
# meta developer: @hikariatama
# scope: inline
# scope: geektg_only

from .. import loader
from telethon.tl.types import Message
from aiogram.types import CallbackQuery
import logging
import asyncio
import time
from math import ceil

logger = logging.getLogger(__name__)


def create_bar(pb):
    try:
        percentage = ceil(pb["progress_ms"] / pb["item"]["duration_ms"] * 100)
        bar_filled = ceil(percentage / 10)
        bar_empty = 10 - bar_filled
        bar = "".join("─" for _ in range(bar_filled))
        bar += "🞆"
        bar += "".join("─" for _ in range(bar_empty))

        bar += f' {pb["progress_ms"] // 1000 // 60:02}:{pb["progress_ms"] // 1000 % 60:02} /'
        bar += f' {pb["item"]["duration_ms"] // 1000 // 60:02}:{pb["item"]["duration_ms"] // 1000 % 60:02}'
    except Exception:
        bar = "──────🞆─── 0:00 / 0:00"

    return bar


@loader.tds
class InlineSpotifyMod(loader.Module):
    """EXTENSION for SpotifyNow mod, that allows you to send interactive player."""

    strings = {"name": "InlineSpotify"}

    def get(self, *args) -> dict:
        return self.db.get(self.strings["name"], *args)

    def set(self, *args) -> None:
        return self.db.set(self.strings["name"], *args)

    async def _reload_sp(self, once=False) -> None:
        while True:
            for mod in self.allmodules.modules:
                if mod.strings("name") == "SpotifyNow":
                    self.sp = mod.sp
                    break

            if once:
                break

            await asyncio.sleep(10)

    async def client_ready(self, client, db) -> None:
        self.db = db
        self.client = client
        self.sp = None

        self._tasks = [asyncio.ensure_future(self._reload_sp())]
        await self._reload_sp(True)

        self._active_forms = []

        if not self.sp:
            raise Exception(
                "Install fucking SpotifyNow, this module is just an extension!"
            )

    async def on_unload(self) -> None:
        for task in self._tasks:
            task.cancel()

    async def inline_close(self, call: CallbackQuery) -> None:
        if call.form["uid"] in self._active_forms:
            self._active_forms.remove(call.form["uid"])

        await call.delete()

    async def sp_previous(self, call: CallbackQuery) -> None:
        self.sp.previous_track()
        await self.inline_iter(call, True)

    async def sp_next(self, call: CallbackQuery) -> None:
        self.sp.next_track()
        await self.inline_iter(call, True)

    async def sp_pause(self, call: CallbackQuery) -> None:
        self.sp.pause_playback()
        await self.inline_iter(call, True)

    async def sp_play(self, call: CallbackQuery) -> None:
        self.sp.start_playback()
        await self.inline_iter(call, True)

    async def sp_shuffle(self, call: CallbackQuery, state: bool) -> None:
        self.sp.shuffle(state)
        await self.inline_iter(call, True)

    async def sp_repeat(self, call: CallbackQuery, state: bool) -> None:
        self.sp.repeat(state)
        await self.inline_iter(call, True)

    async def sp_play_track(self, call: CallbackQuery, query: str) -> None:
        try:
            track = self.sp.track(query)
        except Exception:
            search = self.sp.search(q=query, type="track", limit=1)
            try:
                track = search["tracks"]["items"][0]
            except Exception:
                return

        self.sp.add_to_queue(track["id"])
        self.sp.next_track()

    async def inline_iter(
        self, call: CallbackQuery, once: bool = False, uid: str = False
    ) -> None:
        if not uid:
            uid = call.form["uid"]

        until = time.time() + 5 * 60
        while uid in self._active_forms and until > time.time() or once:
            pb = self.sp.current_playback()
            is_resuming = (
                "actions" in pb
                and "disallows" in pb["actions"]
                and "resuming" in pb["actions"]["disallows"]
                and pb["actions"]["disallows"]["resuming"]
            )

            try:
                artists = [artist["name"] for artist in pb["item"]["artists"]]
            except Exception:
                artists = []

            try:
                track = pb["item"]["name"]
                track_id = pb["item"]["id"]
            except Exception:
                track = ""
                track_id = ""

            keyboard = [
                [
                    {"text": "🔁", "callback": self.sp_repeat, "args": (False,)}
                    if pb["repeat_state"]
                    else {"text": "🔂", "callback": self.sp_repeat, "args": (True,)},
                    {"text": "⏮", "callback": self.sp_previous},
                    {"text": "⏸", "callback": self.sp_pause}
                    if is_resuming
                    else {"text": "▶️", "callback": self.sp_play},
                    {"text": "⏭", "callback": self.sp_next},
                    {"text": "↩️", "callback": self.sp_shuffle, "args": (False,)}
                    if pb["shuffle_state"]
                    else {"text": "🔀", "callback": self.sp_shuffle, "args": (True,)},
                ],
                [
                    {
                        "text": "🔎 Search",
                        "input": "🎧 Enter the name of track",
                        "handler": self.sp_play_track,
                    },
                    {"text": "🔗 Link", "url": f"https://song.link/s/{track_id}"},
                ],
                [{"text": "🚫 Close", "callback": self.inline_close}],
            ]

            text = f"🎧 <b>{', '.join(artists)} - {track}</b>\n<code>{create_bar(pb)}</code><a href='https://song.link/s/{track_id}'>\u206f</a>"

            await call.edit(text, reply_markup=keyboard, disable_web_page_preview=False)

            if once:
                break

            await asyncio.sleep(10)

    async def inline__open(self, call: CallbackQuery) -> None:
        self._tasks += [asyncio.ensure_future(self.inline_iter(call))]

    async def splayercmd(self, message: Message) -> None:
        """Send interactive Spotify player (active only for 5 minutes!)"""
        form_uid = await self.inline.form(
            "<b>🐻 Bear with us, while player is loading...</b>",
            message=message,
            reply_markup=[[{"text": "🎧 Open player", "callback": self.inline__open}]],
            ttl=10 * 60,
        )

        self._active_forms += [form_uid]
