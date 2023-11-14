# Copyright (C) 2023  Nguyễn Tri Phương
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import asyncio
import os

import ensuredeps
import disnake
from disnake.ext import commands


import configuration as cfg

# noinspection PyUnresolvedReferences
import i18n
import logutils

bot = commands.Bot("!c", intents=disnake.Intents.all())


@bot.event
async def on_ready():
    await bot.change_presence(
        activity=disnake.Activity(
            type=disnake.ActivityType.watching, name=cfg.get("general.activity")
        )
    )
    logutils.success(f"changed Discord presence.")
    logutils.success("Started uvicorn web server.")
    logutils.info(
        f"Logged in as {bot.user.name}#{bot.user.discriminator}, ID {bot.user.id}."
    )


def load_modules():
    for m in os.listdir("modules"):
        if "__pycache__" in m:
            continue
        logutils.debug(f"Trying to load {m}")
        if os.path.isdir(f"modules/{m}"):
            bot.load_extension(name=f"modules.{m}", package=f"modules")
            logutils.info(f"-> Loaded module '{m}'.")
        elif m.endswith(".py"):
            bot.load_extension(name=f"modules.{m[:-3]}")
            logutils.info(f"-> Loaded module '{m[:-3]}'.")


def main():
    logutils.set_min_level(logutils.INFO)
    cfg.init_config_hive()
    i18n.init_translation_database()
    logutils.info("Loading modules...")
    load_modules()
    logutils.debug(i18n.translated_string("test", i18n.Locale.VIETNAMESE))
    logutils.debug(i18n.translated_string("test", i18n.Locale.ENGLISH))
    logutils.info("Starting bot...")
    bot.run(cfg.get("credentials.token"))


if __name__ == "__main__":
    main()
