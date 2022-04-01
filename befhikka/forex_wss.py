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

# meta pic: https://img.icons8.com/fluency/50/000000/crowdfunding.png
# meta developer: @hikariatama
# scope: inline_content
# requires: websockets requests

from .. import loader, utils  # noqa
from telethon.tl.types import Message  # noqa
import logging
import websockets
import asyncio
import requests
import time
import json
from urllib.parse import quote_plus
import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import MessageNotModified

logger = logging.getLogger(__name__)


@loader.tds
class RealTimeValutesMod(loader.Module):
    """Track valutes in real time. Updates more than once a second"""
    strings = {
        "name": "RealTimeValutes",
        "loading": "😌 <b>Loading the most actual info from Forex...</b>",
        "wss_error": "🚫 <b>Socket connection error</b>",
        "exchanges": "😌 <b>Exchange rates by Forex</b>\n\n<b>💵 1 USD = {:.2f} RUB\n💶 1 EUR = {:.2f} RUB</b>\n\n<i>This info is relevant to <u>{:%m/%d/%Y %H:%M:%S}</u></i>",
    }

    async def _connect(self) -> None:
        r = await utils.run_sync(requests.get, f'https://rates-live.efxnow.com/signalr/negotiate?clientProtocol=2.1&connectionData=%5B%7B%22name%22%3A%22ratesstreamer%22%7D%5D&_={time.time() * 1000:.0f}')

        token = quote_plus(r.json()['ConnectionToken'])
        base = f"wss://rates-live.efxnow.com/signalr/connect?transport=webSockets&clientProtocol=2.1&connectionToken={token}&connectionData=%5B%7B%22name%22%3A%22ratesstreamer%22%7D%5D&tid=8"

        async with websockets.connect(base) as wss:
            await wss.send('{"H":"ratesstreamer","M":"SubscribeToPricesUpdates","A":[["401203106","401203109"]],"I":8}')  # USD/RUB | EUR/RUB

            self._restart_at = time.time() + 5 * 60

            while time.time() < self._restart_at:
                rates = json.loads(await wss.recv())
                if 'M' not in rates or not rates['M']:
                    continue

                for row in rates['M']:
                    if 'A' not in row:
                        continue

                    rate = row['A']
                    valute = rate[0].split('|')[1].split('/')[0]
                    rate = float(rate[0].split('|')[3])

                    if valute not in self._rates:
                        self._rates[valute] = []
                    
                    if valute not in self._means:
                        self._means[valute] = 0

                    if not self._rates[valute] or abs(rate - self._rates[valute][-1][0]) >= .1:
                        self._rates[valute] += [(rate, round(time.time()))]

                    self._rates[valute] = list(
                        filter(
                            lambda x: x[1] + 2 * 60 * 60 >= time.time(),
                            self._rates[valute]
                        )
                    )

            return await self._connect()

    def get(self, *args) -> dict:
        return self.db.get(self.strings['name'], *args)

    def set(self, *args) -> None:
        return self.db.set(self.strings['name'], *args)

    async def client_ready(self, client, db) -> None:
        self.db = db
        self.client = client
        self._me = (await client.get_me()).id
        self._rates = {}
        self._means = {}
        self._threshold = .03

        self._is_inline = hasattr(self, "inline") and self.inline.init_complete
        self._ratelimit = 0

        self._reload_markup = InlineKeyboardMarkup()
        self._reload_markup.add(
            InlineKeyboardButton(
                "🔄 Update", callback_data="update_exchanges"
            )
        )

        self._task = asyncio.ensure_future(self._connect())

    async def valcmd(self, message: Message) -> None:
        """Show exchange rates"""
        try:
            m = self.strings("exchanges").format(
                self._rates['USD'][-1][0],
                self._rates['EUR'][-1][0],
                getattr(datetime, 'datetime', datetime).fromtimestamp(self._rates['EUR'][-1][1])
            )
        except (KeyError, IndexError):
            await utils.answer(message, self.strings('wss_error'))
            return

        try:
            await self.inline.form(
                m,
                message=message,
                reply_markup=[[{"text": "🔄 Update", "data": "update_exchanges"}]],
            )
        except Exception:
            await utils.answer(message, m)

    async def reload_callback_handler(
        self, call: "aiogram.types.CallbackQuery"  # noqa: F821
    ):
        """
        Processes 'reload' button clicks
        @allow: all
        """
        if call.data != "update_exchanges":
            return

        if self._ratelimit and time.time() < self._ratelimit:
            await call.answer("Do not spam this button")
            return

        self._ratelimit = time.time() + 1

        try:
            await self.inline._bot.edit_message_text(
                inline_message_id=call.inline_message_id,
                text=self.strings("exchanges").format(
                    self._rates['USD'][-1][0],
                    self._rates['EUR'][-1][0],
                    getattr(datetime, 'datetime', datetime).fromtimestamp(self._rates['EUR'][-1][1])
                ),
                reply_markup=self._reload_markup,
                parse_mode="HTML",
            )

            await call.answer("😌 Exchange rates update complete!", show_alert=True)
        except (IndexError, KeyError):
            await call.answer('Socket connection error', show_alert=True)
            return
        except MessageNotModified:
            await call.answer('Exchange rates have not changes since last update', show_alert=True)
            return

    async def on_unload(self) -> None:
        self._task.cancel()
