from .. import loader, utils

@loader.tds
class ReverseMod(loader.Module):
    """Реверс текста."""
    strings = {'name': 'Reverse'}

    async def revcmd(self, message):
        """Используй .rev <текст или реплай>."""
        if message.text:
            text = utils.get_args_raw(message)
            reply = await message.get_reply_message()

            if not text and not reply:
                return await message.edit("Нет текста или реплая.")

            return await message.edit((text or reply.raw_text)[::-1])
        else:
            return await message.edit("Это не текст.")