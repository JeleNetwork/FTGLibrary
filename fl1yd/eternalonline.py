from .. import loader
from asyncio import sleep

@loader.tds
class EternalOnlineMod(loader.Module):
    """Вечный онлайн."""
    strings = {'name': 'Eternal Online'}

    async def client_ready(self, client, db):
        self.db = db

    async def onlinecmd(self, message):
        """Включить вечный онлайн."""
        if not self.db.get("Eternal Online", "status"):
            self.db.set("Eternal Online", "status", True)
            await message.edit("Вечный онлайн включен.")
            while self.db.get("Eternal Online", "status"):
                await message.client(__import__("telethon").functions.account.UpdateStatusRequest(offline=False))
                await sleep(60)

        else:
            self.db.set("Eternal Online", "status", False)
            await message.edit("Вечный онлайн выключен.")