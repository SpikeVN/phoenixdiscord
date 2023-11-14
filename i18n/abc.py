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
import dataclasses
import enum
from typing import Union, Optional

import disnake


@dataclasses.dataclass
class Language:
    """Represents a supported language."""

    native_name: str
    english_name: str
    identifier: str
    discord_locale: Optional[disnake.Locale]


class Locale(enum.Enum):
    """The supported language list."""

    VIETNAMESE: Language = Language("Tiếng Việt", "Vietnamese", "vi", disnake.Locale.vi)
    ENGLISH: Language = Language("English", "English", "en-US", disnake.Locale.en_US)
    SKELETON: Language = Language(
        "skeleton lang", "skeleton_debug_language", "skeleton", None
    )
    DEUTSCH: Language = Language("Deutsch", "German", "de", disnake.Locale.de)
    RUSSIAN: Language = Language("русский язык", "Russian", "ru", disnake.Locale.ru)
    JAPANESE: Language = Language("日本語", "Japanese", "ja", disnake.Locale.ja)
    KOREAN: Language = Language("한국어", "Korean", "ko", disnake.Locale.ko)
    SPANISH: Language = Language("Español", "Spanish", "es-ES", disnake.Locale.es_ES)
    FRENCH: Language = Language("Français", "French", "fr", disnake.Locale.fr)
    LIEM: Language = Language("Ông Liêm", "Ligma", "ol", None)


def get_locale(_i: Union[str, disnake.Locale]):
    for i in Locale:
        if i.value.identifier == str(_i):
            return i
    else:
        raise KeyError(f"Locale with identifier '{_i}' not found.")
