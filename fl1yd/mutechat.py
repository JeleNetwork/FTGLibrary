from .. import loader, utils
from telethon.tl.types import ChatBannedRights as cb
from telethon.tl.functions.messages import EditChatDefaultBannedRightsRequest as br


@loader.tds
class MuteChatMod(loader.Module):
    """Мут чата."""
    strings = {'name': 'MuteChat'}
    
    async def client_ready(self, message, db):
        self.db = db
        
    async def mccmd(self, message):
        """Включить/выключить мут чата."""
        if utils.get_args_raw(message) == "clearall":
            self.db.set("MuteChat", "mc", [])
            return await message.edit("Отключено во всех чатах.")
        if not message.is_private:
            chat = await message.get_chat()
            if not chat.admin_rights and not chat.creator:
                return await message.edit("Я не админ здесь.")
            else:
                if chat.admin_rights.ban_users == False:
                    return await message.edit("У меня нет нужных прав.")
            mc = self.db.get("MuteChat", "mc", [])
            chatid = str(message.chat_id)
            if chatid in mc:
                await message.client(br(message.chat_id, cb(until_date=None, send_messages=None)))
                mc.remove(chatid)
                self.db.set("MuteChat", "mc", mc)
                return await message.edit("Все могут сводобно общаться.")
            else:
                await message.client(br(message.chat_id, cb(until_date=0, send_messages=True)))
                mc.append(chatid)
                self.db.set("MuteChat", "mc", mc)
                await message.edit("Все в муте, кроме админов.")
        else: return await message.edit("Это не чат!") 