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

# meta pic: https://img.icons8.com/fluency/48/000000/cat-head.png
# meta developer: @hikariatama
# scope: non_heroku
# scope: ffmpeg
# requires: pydub python-ffmpeg

from .. import loader, utils
import requests
import random
import io
from pydub import AudioSegment
from telethon.tl.types import Message


@loader.tds
class KeywordMod(loader.Module):
    """Sends purr-r message"""

    strings = {"name": "Purr"}

    async def client_ready(self, client, db):
        self.db = db
        self.client = client

    @loader.unrestricted
    async def purrcmd(self, message: Message) -> None:
        """Sends 'purr' voice message"""
        args = utils.get_args_raw(message) or "<i>🐈 Purrr-r-r-r...</i>"
        purrs = [
            "https://x0.at/ne6O.mp3",
            "https://x0.at/Kc0L.mp3",
            "https://x0.at/rGdI.mp3",
            "https://x0.at/3mtz.mp3",
            "https://x0.at/3U9J.mp3",
        ]

        voice = (await utils.run_sync(requests.get, random.choice(purrs))).content

        byte = io.BytesIO(b"0")
        segm = AudioSegment.from_file(io.BytesIO(voice))
        random_duration = random.randint(5000, 15000)
        end = len(segm) - random_duration
        end = len(segm) if end < 0 else end
        random_begin = random.randint(0, end)
        random_begin = 0 if end < 0 else random_begin
        segm[random_begin : min(len(segm), random_begin + random_duration)].export(
            byte, format="ogg"
        )
        byte.name = "purr.ogg"
        await self.client.send_file(
            message.peer_id,
            byte,
            caption=args,
            voice_note=True,
            reply_to=message.reply_to_msg_id,
        )
        await message.delete()
