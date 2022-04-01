from .. import loader

from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest


@loader.tds
class LeaveJoinMod(loader.Module):
    strings = {"name": "LeaveJoin"}

    async def leavejoincmd(self, message):
        if not (message.is_group and message.is_channel):
            return await message.edit("Это не чат!")

        try:
            await message.client(LeaveChannelRequest(message.chat_id))
            await message.client(JoinChannelRequest(message.chat_id))
        except Exception:
            return await message.edit("Произошла ошибка")

        return await message.delete()