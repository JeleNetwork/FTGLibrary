from .. import loader, utils
from telethon.tl.types import ChatBannedRights as cb
from telethon.tl.functions.channels import EditBannedRequest as eb


@loader.tds
class AntiRaidMod(loader.Module):
    """Режим АнтиРейд."""
    strings = {'name': 'AntiRaid'}
    
    async def client_ready(self, client, db):
        self.db = db
        
    async def antiraidcmd(self, message):
        """Включить/выключить режим AntiRaid. Использование: .antiraid <clearall* (по желанию)>.\n* - выключает режим во всех чатах!"""
        ar = self.db.get("AntiRaid", "ar", [])
        sets = self.db.get("AntiRaid", "sets", {})
        args = utils.get_args_raw(message)

        if args == "clearall":
            self.db.set("AntiRaid", "ar", {})
            self.db.set("AntiRaid", "action", {})
            return await message.edit("<b>[AntiRaid]</b> Режим выключен во всех чатах.")

        if not message.is_private:
            chat = await message.get_chat() 
            if not chat.admin_rights and not chat.creator:
                return await message.edit("<b>Я не админ здесь.</b>")
            else:
                if chat.admin_rights.ban_users == False:
                    return await message.edit("<b>У меня нет нужных прав.</b>") 
 
            chatid = str(message.chat_id)
            if chatid not in ar:
                ar.append(chatid)
                sets.setdefault(chatid, {})
                sets[chatid].setdefault("stats", 0)
                sets[chatid].setdefault("action", "kick")
                self.db.set("AntiRaid", "ar", ar)
                self.db.set("AntiRaid", "sets", sets)
                return await message.edit("<b>[AntiRaid]</b> Активирован в этом чате.")

            else:
                ar.remove(chatid)
                sets.pop(chatid)
                self.db.set("AntiRaid", "ar", ar) 
                self.db.set("AntiRaid", "sets", sets) 
                return await message.edit("<b>[AntiRaid]</b> Деактивирован в этом чате.")

        else:
            return await message.edit("<b>[AntiRaid]</b> Это не чат!")


    async def swatscmd(self, message):
        """Настройки модуля AntiRaid. Использование: .swats <kick/ban/mute/clear>; ничего."""
        if not message.is_private:
            ar = self.db.get("AntiRaid", "ar", [])
            sets = self.db.get("AntiRaid", "sets", {})
            chatid = str(message.chat_id)
            args = utils.get_args_raw(message)
            if chatid in ar:
                if args:
                    if args == "kick":
                        sets[chatid].update({"action": "kick"})
                    elif args == "ban":
                        sets[chatid].update({"action": "ban"})
                    elif args == "mute":
                        sets[chatid].update({"action": "mute"})
                    elif args == "clear":
                        sets[chatid].pop("stats")
                        self.db.set("AntiRaid", "sets", sets)
                        return await message.edit(f"<b>[AntiRaid - Settings]</b> Статистика чата сброшена.")
                    else:
                        return await message.edit("<b>[AntiRaid - Settings]</b> Такого режима нет в списке.\nДоступные режимы: kick/ban/mute.")

                    self.db.set("AntiMention", "sets", sets)
                    return await message.edit(f"<b>[AntiRaid - Settings]</b> Теперь при входе участников будет выполняться действие: {sets[chatid]['action']}.")
                else:
                    return await message.edit(f"<b>[AntiRaid - Settings]</b> Настройки чата:\n\n"
                                            f"<b>Состояние режима:</b> True\n"
                                            f"<b>При входе участников будет выполняться действие:</b> {sets[chatid]['action']}\n"
                                            f"<b>Всего пользователей:</b> {sets[chatid]['stats']}") 
            else:
                return await message.edit("<b>[AntiRaid - Settings]</b> В этом чате режим деактивирован.")
        else:
            return await message.edit("<b>[AntiRaid]</b> Это не чат!")


    async def watcher(self, message):
        """аэахахаээа блять"""
        try:
            ar = self.db.get("AntiRaid", "ar", [])
            sets = self.db.get("AntiRaid", "sets", {})
            chatid = str(message.chat_id)
            if chatid not in ar: return

            if message.user_joined or message.user_added:
                user = await message.get_user()
                if sets[chatid]["action"] == "kick":
                    await message.client.kick_participant(int(chatid), user.id)
                elif sets[chatid]["action"] == "ban":
                    await message.client(eb(int(chatid), user.id, cb(until_date=None, view_messages=True)))
                elif sets[chatid]["action"] == "mute":
                    await message.client(eb(int(chatid), user.id, cb(until_date=True, send_messages=True)))
                sets[chatid].update({"stats": sets[chatid]["stats"] + 1})
                return self.db.set("AntiRaid", "sets", sets)
        except: pass