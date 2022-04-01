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

# meta pic: https://img.icons8.com/external-wanicon-flat-wanicon/64/000000/external-artist-professions-avatar-wanicon-flat-wanicon.png
# meta developer: @hikariatama
# scope: non_heroku

from .. import loader, utils  # noqa
from telethon.tl.types import Message  # noqa
import logging

from PIL import Image
import io
import base64
import requests
import asyncio
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# requires: requests Pillow

logger = logging.getLogger(__name__)


def im_2_b64(image):
    buff = io.BytesIO()
    image.save(buff, format="JPEG")
    p = base64.b64encode(buff.getvalue())
    return p if isinstance(p, str) else p.decode("utf-8")


async def upload(base: str) -> str:
    r = await utils.run_sync(
        requests.post,
        "https://access1.imglarger.com/PhoAi/Upload",
        headers={
            "Host": "access1.imglarger.com",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
            "Content-Type": "application/json",
            "Sec-GPC": "1",
            "Origin": "https://imagetocartoon.com",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://imagetocartoon.com/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
        },
        json={"type": 10, "base64Image": base},
        verify=False,
        timeout=5,
        proxies={},
    )

    return r.json()["data"]["code"]


async def verify(code: str, retries: int = 0) -> str:
    if retries >= 2:
        return False

    r = (
        await utils.run_sync(
            requests.post,
            "https://access1.imglarger.com/PhoAi/CheckStatus",
            headers={
                "Host": "access1.imglarger.com",
                "Connection": "keep-alive",
                "Content-Length": "29",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "Accept": "application/json, text/plain, */*",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
                "Content-Type": "application/json",
                "Sec-GPC": "1",
                "Origin": "https://imagetocartoon.com",
                "Sec-Fetch-Site": "cross-site",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "https://imagetocartoon.com/",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
            },
            json={"code": code, "type": 10},
            verify=False,
            timeout=15,
            proxies={},
        )
    ).json()

    if r["code"] != 200 or not r["data"]["downloadUrls"][0]:
        await asyncio.sleep(2)
        return await verify(code, retries + 1)

    return r["data"]["downloadUrls"][0]


@loader.tds
class AnimefyMod(loader.Module):
    """Animefies photo from real to anime characters aka cartoons"""

    strings = {
        "name": "Animefy",
        "no_media": "👩‍🎤 <i>Drawer is nothing without the model... Show me the photo!</i>",
        "drawing": "<b>👨‍🎤 Let me draw this cutie! Attempt {}</b>",
        "finish": "<b>👨‍🎤 Finally, I'm the real artist.</b>",
        "err": "<b>👩‍🎨 My skills are insufficient to draw this person. Try again or pick another photo 😌</b>",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            "max_retries", 3, lambda: "How many times to try on unsuccess"
        )

    def get(self, *args) -> dict:
        return self.db.get(self.strings["name"], *args)

    def set(self, *args) -> None:
        return self.db.set(self.strings["name"], *args)

    async def client_ready(self, client, db) -> None:
        self.db = db
        self.client = client

    async def animefycmd(self, message: Message, retries: int = 0) -> None:
        """<reply> - Animefy photo"""
        reply = await message.get_reply_message()
        media = (
            message.media
            if getattr(message, "photo", False)
            else (reply.media if reply else None)
        )
        if not media:
            await utils.answer(message, self.strings("no_media"))
            return

        message = await utils.answer(
            message, self.strings("drawing").format(retries + 1)
        )
        if isinstance(message, (list, set, tuple)):
            message = message[0]

        photo = await verify(
            await upload(
                im_2_b64(
                    Image.open(
                        io.BytesIO(await self.client.download_file(media, bytes))
                    )
                )
            )
        )

        try:
            await self.client.send_file(
                message.peer_id,
                file=photo,
                caption=self.strings("finish"),
                reply_to=reply,
            )

            if message.out:
                await message.delete()
        except Exception:
            if retries + 1 > self.config["max_retries"]:
                await utils.answer(message, self.strings("err"))
                return

            return await self.animefycmd(message, retries + 1)
