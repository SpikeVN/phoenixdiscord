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
from typing import Union

import disnake
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import configuration as cfg
import i18n.abc
import logutils

cred = credentials.Certificate("credentials.json")
app = firebase_admin.initialize_app(cred)
DB = firestore.client()


def initialize_userdata(user: disnake.User):
    """
    Initializes user data with default value.
    """
    DB.collection("phoenixproject").document(f"uid{user.id}").set(
        {
            "punishments": {"banned": False, "kicked": 0, "warned": 0, "isolated": 0},
            "locale": "vi",
            "dm": True,
        }
    )


class UserPunishments:
    def __init__(self, user: disnake.User):
        self.user: disnake.User = user
        self.punishments = (
            DB.collection("phoenixproject")
            .document(f"uid{user.id}")
            .get(["punishments"])
            .to_dict()
        )["punishments"]
        if tuple(self.punishments.keys()) != ("banned", "isolated", "kicked", "warned"):
            logutils.error(
                f"Faulty user data in database when reading punishments. Resetting users' punishments..."
            )
            DB.collection("phoenixproject").document(f"uid{user.id}").update(
                {
                    "punishments": {
                        "banned": False,
                        "kicked": 0,
                        "warned": 0,
                        "isolated": 0,
                    }
                }
            )

    @property
    def banned(self):
        return self.punishments["banned"]

    @property
    def kicked(self):
        return self.punishments["kicked"]

    @property
    def isolated(self):
        return self.punishments["isolated"]

    @property
    def warned(self):
        return self.punishments["warned"]

    @banned.setter
    def banned(self, value: bool):
        DB.collection("phoenixproject").document(f"uid{self.user.id}").update(
            {"punishments.banned": value}
        )
        self.punishments["banned"] = value

    @kicked.setter
    def kicked(self, value: int):
        DB.collection("phoenixproject").document(f"uid{self.user.id}").update(
            {"punishments.kicked": value}
        )
        self.punishments["kicked"] = value

    @isolated.setter
    def isolated(self, value: int):
        DB.collection("phoenixproject").document(f"uid{self.user.id}").update(
            {"punishments.isolated": value}
        )
        self.punishments["isolated"] = value

    @warned.setter
    def warned(self, value: int):
        DB.collection("phoenixproject").document(f"uid{self.user.id}").update(
            {"punishments.warned": value}
        )
        self.punishments["warned"] = value

    def __getitem__(self, item):
        match item:
            case "warned":
                return self.warned
            case "banned":
                return self.banned
            case "kicked":
                return self.kicked
            case "isolated":
                return self.isolated

    def __setitem__(self, key, value):
        match key:
            case "warned":
                self.warned = value
            case "banned":
                self.banned = value
            case "kicked":
                self.kicked = value
            case "isolated":
                self.isolated = value


class User:
    def __init__(self, base_user: Union[disnake.Member, disnake.User]):
        self.user: disnake.User = base_user
        if (
            DB.collection("phoenixproject")
            .document(f"uid{base_user.id}")
            .get()
            .to_dict()
            is None
        ):
            initialize_userdata(self.user)

    @property
    def punishments(self) -> UserPunishments:
        return UserPunishments(self.user)

    @property
    def locale(self) -> "i18n.Locale":
        try:
            return i18n.abc.get_locale(
                DB.collection("phoenixproject")
                .document(f"uid{self.user.id}")
                .get(["locale"])
                .get("locale")
            )
        except KeyError:
            logutils.error(
                f"Faulty user data in database when reading locale. Resetting user's locale..."
            )
            DB.collection("phoenixproject").document(f"uid{self.user.id}").update(
                {"locale": cfg.get("general.locale")}
            )

    @locale.setter
    def locale(self, value: "i18n.LocaleType"):
        if isinstance(value, disnake.Locale):
            DB.collection("phoenixproject").document(f"uid{self.user.id}").update(
                {"locale": str(value)}
            )
        else:
            DB.collection("phoenixproject").document(f"uid{self.user.id}").update(
                {"locale": value.value.identifier}
            )

    @property
    def accept_direct_message(self) -> bool:
        try:
            return (
                DB.collection("phoenixproject")
                .document(f"uid{self.user.id}")
                .get(["dm"])
                .get("dm")
            )
        except KeyError:
            logutils.error(
                f"Faulty user data in database when reading DM preference. Resetting user's DM preference..."
            )
            DB.collection("phoenixproject").document(f"uid{self.user.id}").update(
                {"locale": True}
            )

    @accept_direct_message.setter
    def accept_direct_message(self, value: bool):
        DB.collection("phoenixproject").document(f"uid{self.user.id}").update(
            {f"locale": value}
        )

    def enable_direct_message(self):
        DB.collection("phoenixproject").document(f"uid{self.user.id}").update(
            {f"locale": True}
        )

    def disable_direct_message(self):
        DB.collection("phoenixproject").document(f"uid{self.user.id}").update(
            {f"locale": False}
        )
