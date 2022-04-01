import io
from .. import loader, utils
from random import randrange as r
from PIL import Image, ImageDraw

@loader.tds 
class HairMod(loader.Module):
    """Волос хаха!!"""
    strings = {'name': 'Hair'}

    async def haircmd(self, message):
        """Волос!"""
        reply = await message.get_reply_message()
        if not reply: return await message.edit("Нет реплая на картинку/стикер.")
        if reply.file.mime_type.split('/')[0] == "image":
            im = Image.open(io.BytesIO(await message.client.download_file(reply, bytes)))
            draw = ImageDraw.Draw(im)
            w, h = im.size
            draw.arc((r(w), r(h), r(w) + r(300), r(h) + r(550)), r(350), 180 + r(350), fill="black", width=1)
            out = io.BytesIO()
            out.name = f"witHair{reply.file.ext}"
            im.save(out)
            out.seek(0) 
            await message.client.send_file(message.to_id, out, reply_to=reply.id if reply else None) 
            await message.delete()
        else: return await message.edit("Это не картинка/стикер.")