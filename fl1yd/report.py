from .. import loader, utils
from telethon import functions

@loader.tds
class ReportMod(loader.Module):
    """Репорт"""
    strings = {"name": "Report"}

    async def reportcmd(self, message):
        """Репорт пользователя за спам."""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if args:
            user = await message.client.get_entity(args if not args.isnumeric() else int(args))
        if reply:
            user = await message.client.get_entity(reply.sender_id)
        else:
            return await message.edit("<b>Кого я должен зарепортить?</b>")

        await message.client(functions.messages.ReportSpamRequest(peer=user.id))
        await message.edit("<b>Ты получил репорт за спам!</b>")