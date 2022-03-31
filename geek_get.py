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

# meta pic: https://img.icons8.com/color/48/000000/trekking.png
# meta developer: @hikariatama

from .. import loader, utils, main, heroku
from telethon.tl.types import Message
import logging
import os
import json
from git import Repo
from git.exc import InvalidGitRepositoryError
from telethon.sessions import StringSession
import collections

api_token_type = collections.namedtuple("api_token", ("ID", "HASH"))

logger = logging.getLogger(__name__)


def get_repo(geek: bool) -> Repo:
    """Helper to get the repo, making it if not found"""
    try:
        repo = Repo(os.path.dirname(utils.get_base_dir()))
    except InvalidGitRepositoryError:
        repo = Repo.init(os.path.dirname(utils.get_base_dir()))
        if geek:
            origin = repo.create_remote(
                "origin", "https://github.com/GeekTG/Friendly-Telegram"
            )
        else:
            origin = repo.create_remote(
                "origin", "https://gitlab.com/friendly-telegram/friendly-telegram"
            )

        origin.fetch()
        if "master" not in repo.heads:
            repo.create_head("master", origin.refs.master)
        repo.heads.master.set_tracking_branch(origin.refs.master)
        repo.heads.master.checkout(True)
    return repo


@loader.tds
class FTGManagerMod(loader.Module):
    """Install GeekTG on FTG or vice-versa"""

    strings = {
        "name": "FTGManager",
        "geek": "🕶 <b>Congrats! You are Geek!</b>\n\n<b>GeekTG version: {}.{}.{}</b>\n<b>Branch: master</b>",
        "geek_beta": "🕶 <b>Congrats! You are Geek!</b>\n\n<b>GeekTG version: {}.{}.{}beta</b>\n<b>Branch: beta</b>\n\n<i>🔮 You're using the unstable branch (<b>beta</b>). You receive fresh but untested updates. Report any bugs to @chat_ftg or @hikari_chat</i>",
        "geek_alpha": "🕶 <b>Congrats! You are Geek!</b>\n\n<b>GeekTG version: {}.{}.{}alpha</b>\n<b>Branch: alpha</b>\n\n<i>🔮 You're using <b><u>very</u></b> unstable branch (<b>alpha</b>). You receive fresh but untested updates. You <b><u>can't ask for help, only report bugs</u></b></i>",
        "ftg": '😔 <b>You\'re on official FTG now!</b>\n<b>Version: <a href="https://gitlab.com/friendly-telegram/friendly-telegram/-/commit/{}">{}</a></b>\n<b>You can install GeekTG using </b><code>{}install_geektg</code>',
        "heroku": "😔 <b>You're on official FTG now!</b>\n<b>Version: ⛎ Heroku</b>\n<b>You can install GeekTG using </b><code>{}install_geektg</code>",
    }

    def get(self, *args) -> dict:
        return self.db.get(self.strings["name"], *args)

    def set(self, *args) -> None:
        return self.db.set(self.strings["name"], *args)

    async def client_ready(self, client, db) -> None:
        self.db = db
        self.client = client
        self.prefix = utils.escape_html(
            (self.db.get(main.__name__, "command_prefix", False) or ".")[0]
        )
        if self.get("installed", False):
            await self.client.send_message(*self.get("edit"))
            self.set("installed", False)

    async def _install_vds(self, message: Message, geek: bool) -> None:
        # Attempt to install Backuper if it is not installed
        if "backupdb" not in self.allmodules.commands:
            await self.allmodules.commands["dlmod"](
                await self.client.send_message(
                    "me", ".dlmod https://mods.hikariatama.ru/backuper.py"
                )
            )

        # If installation was successful, backup database in case of error
        if "backupdb" in self.allmodules.commands:
            await self.allmodules.commands["backupdb"](
                await self.client.send_message("me", ".backupdb")
            )

        self.set("installed", True)
        ver = "GeekTG" if geek else "FTG"
        self.set(
            "edit",
            (
                utils.get_chat_id(message),
                f"🕶 <b>{ver} installation successful! Check version with </b><code>{self.prefix}ftgver</code>",
            ),
        )
        await self.db._backend.do_upload(json.dumps(self.db))

        # Change working directory:
        PATH = "/".join(os.path.dirname(os.path.abspath(main.__file__)).split("/")[:-2])
        os.chdir(PATH)

        installation_dir = os.path.dirname(os.path.abspath(main.__file__)).split("/")[
            -2
        ]

        await message.edit("📇 <b>Backing up files...</b>")
        # Backup api credintials:
        files = {
            "api_token.txt": open(f"{installation_dir}/api_token.txt", "rb").read()
        }
        # Backup sessions:
        for file in os.scandir(installation_dir):
            if file.path.endswith(".session"):
                f = file.path.split("/")[-1]
                files[f] = open(os.path.join(installation_dir, f), "rb").read()

        if geek:
            # Uninstall Telethon:
            await message.edit("📤 <b>Uninstalling Telethon...</b>")
            os.popen("pip3 uninstall -y telethon").read()

            await message.edit("📥 <b>Installing Telethon-Mod...</b>")
            # Install Telethon-mod:
            os.popen("pip3 install -U --force-reinstall telethon-mod").read()
        else:
            # Uninstall Telethon-Mod:
            await message.edit("📤 <b>Uninstalling Telethon-Mod...</b>")
            os.popen("pip3 uninstall -y telethon-mod").read()

            await message.edit("📥 <b>Installing Telethon...</b>")
            # Install Telethon-mod:
            os.popen("pip3 install -U --force-reinstall telethon").read()

        if geek:
            await message.edit("🪄 <b>Cloning GeekTG repository...</b>")
        else:
            await message.edit("🪄 <b>Cloning FTG repository...</b>")

        # Move old files into new directory:
        os.popen(f"mv {installation_dir} friendly-telegram-old").read()
        # Clone repository:
        if geek:
            os.popen(
                f"git clone https://github.com/GeekTG/Friendly-Telegram {installation_dir}"
            ).read()
        else:
            os.popen(
                f"git clone https://gitlab.com/friendly-telegram/friendly-telegram {installation_dir}"
            ).read()

        for filename, content in files.items():  # Return auth files
            open(f"{installation_dir}/{filename}", "wb").write(content)

        await message.edit(f"🕶 <b>{ver} installed! Fully restarting userbot...</b>")

        os.chdir(os.path.join(PATH, installation_dir))  # Change directory back

        await self.allmodules.commands["restart"](message)

    async def _install_heroku(self, message: Message, geek: bool) -> None:
        self.set("installed", True)
        self.set(
            "edit",
            (
                utils.get_chat_id(message),
                f"🕶 <b>Installation successful! Check version with </b><code>{self.prefix}ftgver</code>",
            ),
        )
        await self.db._backend.do_upload(json.dumps(self.db))

        ver = "GeekTG" if geek else "FTG"
        await message.edit(
            f"⛎ <b>Performing Heroku install. Updating {ver} buildpacks...</b>"
        )

        key = os.environ["heroku_api_token"]

        # Remember old app
        old_app, old_config = heroku.get_app(
            authorization_strings=os.environ["authorization_strings"],
            key=key,
            api_token=None,
            create_new=False,
            full_match=True,
        )

        # Create new heroku app
        app, config = heroku.get_app(
            authorization_strings=None,
            key=key,
            api_token=api_token_type(self.client.api_id, self.client.api_hash),
            create_new=True,
            full_match=True,
        )

        # Determine which buildpacks do we need
        if geek:
            buildpacks = [
                "https://github.com/heroku/heroku-buildpack-python",
                "https://github.com/GeekTG/Heroku-BuildPack",
                "https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest",
            ]
        else:
            buildpacks = [
                "https://github.com/heroku/heroku-buildpack-python",
                "https://gitlab.com/friendly-telegram/heroku-buildpack",
            ]

        await message.edit(
            f"⛎ <b>Installing {ver} on Heroku...</b>\n<i>This process will take several minutes, be patient!</i>"
        )

        # Fill config
        data = json.dumps(
            {
                getattr(client, "phone", ""): StringSession.save(client.session)
                for client in self.allclients
            }
        )
        config["authorization_strings"] = data
        config["heroku_api_token"] = key
        config["api_hash"] = self.client.api_hash
        config["api_id"] = self.client.api_id

        # Apply buildpacks
        app.update_buildpacks(buildpacks)

        # Fetch repo
        repo = get_repo(geek)
        url = app.git_url.replace("https://", "https://api:" + key + "@")
        if "heroku" in repo.remotes:
            remote = repo.remote("heroku")
            remote.set_url(url)
        else:
            remote = repo.create_remote("heroku", url)

        remote.push(refspec="HEAD:refs/heads/master")

        # Start new app processes
        app.batch_scale_formation_processes(
            {
                "web": 1,
                "worker-DO-NOT-TURN-ON-OR-THINGS-WILL-BREAK": 0,
                "restarter-DO-NOT-TURN-ON-OR-THINGS-WILL-BREAK": 0,
            }
        )

        # Stop current app
        old_app.batch_scale_formation_processes(
            {
                "web": 0,
                "worker-DO-NOT-TURN-ON-OR-THINGS-WILL-BREAK": 0,
                "restarter-DO-NOT-TURN-ON-OR-THINGS-WILL-BREAK": 0,
            }
        )

    async def install_geektgcmd(self, message: Message) -> None:
        """Install GeekTG"""
        if getattr(main, "__version__", False):
            await message.edit(
                "🕶 <b>You're already Geek! No need to execute this command</b>"
            )
            return

        if not os.environ.get("DYNO", False):
            await self._install_vds(message, geek=True)
        else:
            await self._install_heroku(message, geek=True)

    async def install_official_ftgcmd(self, message: Message) -> None:
        """Install official FTG"""
        if not getattr(main, "__version__", False):
            await message.edit(
                "🕶 <b>You're not Geek! No need to execute this command</b>"
            )
            return

        if not os.environ.get("DYNO", False):
            await self._install_vds(message, geek=False)
        else:
            await self._install_heroku(message, geek=False)

    @loader.unrestricted
    async def ftgvercmd(self, message: Message) -> None:
        """Get current Userbot type (Geek/Official) and version"""
        if version := getattr(main, "__version__", False):
            branch = os.popen("git rev-parse --abbrev-ref HEAD").read()
            if "beta" in branch:
                await utils.answer(message, self.strings("geek_beta").format(*version))
            elif "alpha" in branch:
                await utils.answer(message, self.strings("geek_alpha").format(*version))
            else:
                await utils.answer(message, self.strings("geek").format(*version))

        elif commit := os.popen('git log -1 --format="%H"').read():
            await utils.answer(
                message, self.strings("ftg").format(commit, commit[:7], self.prefix)
            )
        else:
            await utils.answer(message, self.strings("heroku").format(self.prefix))
