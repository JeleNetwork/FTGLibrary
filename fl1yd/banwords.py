import requests
from .. import utils, loader
from telethon.tl.types import ChatBannedRights as cb
from telethon.tl.functions.channels import EditBannedRequest as eb


@loader.tds 
class BanWordsMod(loader.Module):
    """Плохие слова."""
    strings = {'name': 'BanWords'}

    async def client_ready(self, client, db):
        self.db = db

    async def addbwcmd(self, message):
        """Добавить слово в список "Плохих слов". Используй: .addbw <слово>."""
        if not message.is_private:
            chat = await message.get_chat()
            if not chat.admin_rights and not chat.creator:
                return await message.edit("<b>Я не админ здесь.</b>")
            else:
                if chat.admin_rights.delete_messages == False:
                    return await message.edit("<b>У меня нет нужных прав.</b>")
        words = self.db.get("BanWords", "bws", {})
        args = utils.get_args_raw(message).lower()
        if not args: return await message.edit("<b>[BanWords]</b> Нет аргументов.")
        chatid = str(message.chat_id)
        if chatid not in words:
            words.setdefault(chatid, [])
        if "stats" not in words:
            words.setdefault("stats", {}) 
            words["stats"].setdefault(chatid, {})
            words["stats"][chatid].setdefault("action", "none")
            words["stats"][chatid].setdefault("antimat", False)
            words["stats"][chatid].setdefault("limit", 5)

        if args not in words[chatid]:
            if ", " in args:
                args = args.split(', ')
                words[chatid].extend(args)
                self.db.set("BanWords", "bws", words)
                await message.edit(f"<b>[BanWords]</b> В список чата добавлены слова - \"<code>{'; '.join(args)}</code>\".")
            else:
                words[chatid].append(args)
                self.db.set("BanWords", "bws", words)
                await message.edit(f"<b>[BanWords]</b> В список чата добавлено слово - \"<code>{args}</code>\".")
        else: return await message.edit("<b>[BanWords]</b> Такое слово уже есть в списке слов чата.")
    
    
    async def rmbwcmd(self, message):
        """Удалить слово из список "Плохих слов". Используй: .rmbw <слово или all/clearall (по желанию)>.\nall - удаляет все слова из списка.\nclearall - удаляет все сохраненные данные модуля."""
        words = self.db.get("BanWords", "bws", {})
        args = utils.get_args_raw(message) 
        if not args: return await message.edit("<b>[BanWords]</b> Нет аргументов.")
        chatid = str(message.chat_id)
        try:
            if args == "all":
                words.pop(chatid) 
                words["stats"].pop(chatid) 
                self.db.set("BanWords", "bws", words) 
                return await message.edit("<b>[BanWords]</b> Из списка чата удалены все слова.")
            if args == "clearall":
                self.db.set("BanWords", "bws", {}) 
                return await message.edit("<b>[BanWords]</b> Все списки из всех чатов были удалены.")
            words[chatid].remove(args)
            if len(words[chatid]) == 0:
                words.pop(chatid)
            self.db.set("BanWords", "bws", words)
            await message.edit(f"<b>[BanWords]</b> Из списка чата удалено слово - \"<code>{args}</code>\".")
        except (KeyError, ValueError): return await message.edit("<b>[BanWords]</b> Этого слова нет в словаре этого чата.") 
        
    
    async def bwscmd(self, message):
        """Посмотреть список "Плохих слов". Используй: .bws."""
        words = self.db.get("BanWords", "bws", {})
        chatid = str(message.chat_id)
        try: 
            ls = words[chatid]
            if len(ls) == 0: raise KeyError
        except KeyError: return await message.edit("<b>[BanWords]</b> В этом чате нет списка слов.")
        word = ""
        for _ in ls:
            word += f"• <code>{_}</code>\n"
        await message.edit(f"<b>[BanWords]</b> Список слов в этом чате:\n\n{word}") 
        
        
    async def bwstatscmd(self, message):
        """Статистика "Плохих слов". Используй: .bwstats <clear* (по желанию)>.\n* - сбросить настройки чата."""
        words = self.db.get("BanWords", "bws", {}) 
        chatid = str(message.chat_id)
        args = utils.get_args_raw(message)
        if args == "clear":
            try:
                words["stats"].pop(chatid)
                words["stats"].setdefault(chatid, {})
                words["stats"][chatid].setdefault("antimat", False)
                words["stats"][chatid].setdefault("action", "none")
                words["limit"][chatid].setdefault("limit", 5)
                self.db.set("BanWords", "bws", words) 
                return await message.edit("<b>[BanWords]</b> Настройки чата сброшены.")
            except KeyError: return await message.edit("<b>[BanWords]</b> Нет статистики пользователей.")
        try:
            w = "" 
            for _ in words["stats"][chatid]:
                if _ not in ["action", "antimat", "limit"] and words["stats"][chatid][_] != 0:
                    user = await message.client.get_entity(int(_)) 
                    w += f'• <a href="tg://user?id={int(_)}">{user.first_name}</a>: <code>{words["stats"][chatid][_]}</code>\n'
            return await message.edit(f"<b>[BanWords]</b> Кто использовал спец.слова:\n\n{w}") 
        except KeyError: return await message.edit("<b>[BanWords]</b> В этом чате нет тех, кто использовал спец.слова.")
        
    
    async def swbwcmd(self, message):
        """Переключить режим "Плохих слов". Используй: .swbw <режим(antimat/kick/ban/mute/none)>, или .swbw limit <кол-во:int>."""
        if not message.is_private:
            chat = await message.get_chat()
            if not chat.admin_rights and not chat.creator:
                return await message.edit("<b>Я не админ здесь.</b>")
            else:
                if chat.admin_rights.delete_messages == False:
                    return await message.edit("<b>У меня нет нужных прав.</b>")
        words = self.db.get("BanWords", "bws", {})
        args = utils.get_args_raw(message)
        chatid = str(message.chat_id)

        if chatid not in words:
            words.setdefault(chatid, [])
        if "stats" not in words:
            words.setdefault("stats", {}) 
            words["stats"].setdefault(chatid, {})
            words["stats"][chatid].setdefault("action", "none")
            words["stats"][chatid].setdefault("antimat", False)
            words["stats"][chatid].setdefault("limit", 5)
        if args:
            if "limit" in args:
                try:
                    limit = int(utils.get_args_raw(message).split(' ', 1)[1])
                    words["stats"][chatid].update({"limit": limit})
                    self.db.set("BanWords", "bws", words)
                    return await message.edit(f"<b>[BanWords]</b> Лимит спец.слов был установлен на {words['stats'][chatid]['limit']}.")
                except (IndexError, ValueError): return await message.edit(f"<b>[BanWords]</b> Лимит спец.слов в этом чате - {words['stats'][chatid]['limit']}\nУстановить новый можно командой .bwsw limit <кол-во:int>.")
            if args == "antimat":
                if words["stats"][chatid]["antimat"] == False:
                    words["stats"][chatid]["antimat"] = True
                    self.db.set("BanWords", "bws", words)
                    return await message.edit("<b>[BanWords]</b> Режим \"антимат\" включен.")
                else:
                    words["stats"][chatid]["antimat"] = False
                    self.db.set("BanWords", "bws", words)
                    return await message.edit("<b>[BanWords]</b> Режим \"антимат\" выключен.")
            else:
                if args == "kick":
                    words["stats"][chatid].update({"action": "kick"})
                elif args == "ban":
                    words["stats"][chatid].update({"action": "ban"})
                elif args == "mute":
                    words["stats"][chatid].update({"action": "mute"})
                elif args == "none":
                    words["stats"][chatid].update({"action": "none"})
                else: return await message.edit(f"<b>[BanWords]</b> Такого режима нет в списке. Есть: kick/ban/mute/none.")
                self.db.set("BanWords", "bws", words)
                return await message.edit(f"<b>[BanWords]</b> Теперь при достижении лимита спец.слов будет выполняться действие: {words['stats'][chatid]['action']}.")
        else: return await message.edit(f"<b>[BanWords]</b> Настройки чата:\n\n"
                                        f"<b>Лимит спец.слов:</b> {words['stats'][chatid]['limit']}\n"
                                        f"<b>При достижении лимита спец.слов будет выполняться действие:</b> {words['stats'][chatid]['action']}\n"
                                        f"<b>Статус режима \"антимат\":</b> {words['stats'][chatid]['antimat']}") 
            
            
    async def watcher(self, message):
        """Обновление от 4.01: Переделал модуль."""
        try:
            if message.sender_id == (await message.client.get_me()).id: return
            words = self.db.get("BanWords", "bws", {})
            chatid = str(message.chat_id)
            userid = str(message.sender_id) 
            user = await message.client.get_entity(int(userid)) 
            if chatid not in str(words): return
            action = words["stats"][chatid]["action"] 
            if words["stats"][chatid]["antimat"] == True:
                r = requests.get("https://api.fl1yd.ml/badwords")
                ls = r.text.split(', ')
            else: 
                ls = words[chatid]
            for _ in ls:
                if _.lower() in message.text.lower().split():
                    if userid not in words["stats"][chatid]:
                        words["stats"][chatid].setdefault(userid, 0)
                    count = words["stats"][chatid][userid]
                    words["stats"][chatid].update({userid: count + 1})
                    self.db.set("BanWords", "bws", words)
                    if count == words["stats"][chatid]["limit"]:
                        try:
                            if action != "none":
                                if action == "kick":
                                    await message.client.kick_participant(int(chatid), int(userid))
                                elif action == "ban":
                                    await message.client(eb(int(chatid), userid, cb(until_date=None, view_messages=True)))
                                elif action == "mute":
                                    await message.client(eb(int(chatid), user.id, cb(until_date=True, send_messages=True)))
                                words["stats"][chatid].pop(userid) 
                                self.db.set("BanWords", "bws", words) 
                                await message.respond(f"<b>[BanWords]</b> {user.first_name} достиг лимит ({words['stats'][chatid]['limit']}) спец.слова, и был ограничен в чате.")
                            else: pass 
                        except: pass
                    await message.client.delete_messages(message.chat_id, message.id)
        except: pass