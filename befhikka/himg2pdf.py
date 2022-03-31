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

# meta pic: https://img.icons8.com/fluency/48/000000/pdf-mail.png
# meta developer: @hikariatama
# scope: non_heroku
# requires: Pillow

from .. import loader, utils
from PIL import Image, UnidentifiedImageError
import io
import logging
from telethon.tl.types import Message

logger = logging.getLogger(__name__)


@loader.tds
class Img2PdfMod(loader.Module):
    """Packs images to pdf"""

    strings = {"name": "Img2Pdf"}

    async def client_ready(self, client, db):
        self.db = db
        self.client = client

    @loader.unrestricted
    async def img2pdfcmd(self, message: Message) -> None:
        """<filename | optional> - Pack images into pdf"""
        try:
            start_offset = (
                message.id if message.media else (await message.get_reply_message()).id
            )
        except Exception:
            return await utils.answer(message, self.strings("no_file"))

        images = []

        async for ms in self.client.iter_messages(
            message.peer_id, offset_id=start_offset - 1, reverse=True
        ):
            if not ms.media:
                break
            im = await self.client.download_file(ms.media)
            try:
                images.append(Image.open(io.BytesIO(im)))
            except UnidentifiedImageError:
                break

        first_image, images = images[0], images[1:]
        file = io.BytesIO()
        first_image.save(
            file, "PDF", resolution=100.0, save_all=True, append_images=images
        )
        f = io.BytesIO(file.getvalue())
        f.name = utils.get_args_raw(message) or "packed_images.pdf"
        await self.client.send_file(message.peer_id, f)
        await message.delete()
