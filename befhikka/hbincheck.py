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

# meta pic: https://img.icons8.com/fluency/48/000000/bank-card-back-side.png
# meta developer: @hikariatama

from .. import loader, utils
import requests
import json
from telethon.tl.types import Message


@loader.tds
class BinCheckerMod(loader.Module):
    """Show bin info about card"""

    strings = {
        "name": "BinCheck",
        "args": "💳 <b>To get bin info, you need to specify Bin of card (first 6 digits)</b>",
    }

    async def client_ready(self, client, db):
        self.db = db
        self.client = client

    @loader.unrestricted
    async def bincheckcmd(self, message: Message) -> None:
        """[bin] - Get card Bin info"""
        args = utils.get_args_raw(message)
        try:
            args = int(args)
            if args < 100000 or args > 999999:
                raise Exception()
        except Exception:
            await utils.answer(message, self.strings("args"))
            return

        async def bincheck(cc):
            try:
                ans = json.loads(
                    (
                        await utils.run_sync(
                            requests.get, f"https://bin-checker.net/api/{str(cc)}"
                        )
                    ).text
                )

                return (
                    "<b><u>Bin: %s</u></b>\n<code>\n🏦 Bank: %s\n🌐 Payment system: %s [%s]\n✳️ Level: %s\n⚛️ Country: %s </code>"
                    % (
                        cc,
                        ans["bank"]["name"],
                        ans["scheme"],
                        ans["type"],
                        ans["level"],
                        ans["country"]["name"],
                    )
                )
            except:
                return "BIN data unavailable"

        await utils.answer(message, await bincheck(args))
