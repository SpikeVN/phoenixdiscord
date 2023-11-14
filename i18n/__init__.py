# Copyright (c) 2022-2023 SpikeBonjour
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


"""
Apes localization engine.
"""

import json
import os
import random

import database
import logutils
from .abc import *
from .checker import check_structure


class LocalizationError(Exception):
    pass


LOCALIZATION_DATA: dict[Locale, dict[str, dict]] = {}
LocaleType = Union[Locale, disnake.Locale]
AVALIABLE_LOCALES = {
    "Tiếng Việt - Việt Nam": "vi",
    "English - United States": "en-US",
    "Deutsch - Deutschland": "de",
    "русский язык - Россия": "ru",
    "日本語 - 日本": "ja",
    "한국어 - 대한민국": "ko",
    "Español - España": "es-ES",
    "Français - République française": "fr",
    "Ông Liêm - 11 Anh 1": "ol",
}


def init_translation_database():
    logutils.info("Initializing localization database...")
    global LOCALIZATION_DATA
    for lan in os.listdir("i18n/translations"):
        if lan.endswith(".json"):
            with open(f"i18n/translations/{lan}", "r", encoding="utf8") as f:
                LOCALIZATION_DATA[get_locale(lan[:-5])] = json.loads(f.read())
                logutils.debug(f"Loaded language {lan[:-5]} from {lan}")
    logutils.success("Localization initialization successful.")


def translated_string(
    _i: str, locale: Union[LocaleType, str, disnake.User, disnake.Member]
) -> str:
    path = _i.split(".")
    loc = None
    if isinstance(locale, Locale):
        loc = locale
    elif isinstance(locale, disnake.Locale) or isinstance(locale, str):
        loc = abc.get_locale(locale)
    elif isinstance(locale, disnake.User) or isinstance(locale, disnake.Member):
        loc = database.User(locale).locale
    else:
        raise ValueError(f"Unsupported locale {locale}")
    a = LOCALIZATION_DATA[loc].copy()
    try:
        for i in path:
            a = a[i]
        if isinstance(a, list):
            return random.choice(a)
        return a  # type: ignore
    except KeyError:
        raise LocalizationError(f"Localized string not found: {_i}")


def localized_command_description(cmd: str) -> disnake.Localized:
    data = {}
    for k, v in LOCALIZATION_DATA.items():
        if k.value.discord_locale is not None:
            data[k.value.discord_locale] = (
                v.get("commands").get(cmd).get("commandDescription")
            )
    return disnake.Localized(
        LOCALIZATION_DATA[Locale.ENGLISH]["commands"][cmd]["commandDescription"],
        data=data,
    )


def localized_argument_description(cmd: str, argument_name: str) -> disnake.Localised:
    data = {}
    for k, v in LOCALIZATION_DATA.items():
        if k.value.discord_locale is not None:
            data[k.value.discord_locale] = (
                v.get("commands").get(cmd).get("argumentDescription").get(argument_name)
            )
    return disnake.Localized(
        LOCALIZATION_DATA[Locale.ENGLISH]["commands"][cmd]["argumentDescription"][
            argument_name
        ],
        data=data,
    )
