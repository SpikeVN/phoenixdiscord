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

import os

import yaml

import gcloud_helper
import logutils

CONFIG_HIVE: dict = {}
ONLINE_HIVE: dict = {}


def init_config_hive():
    """Initialize the RAM config storage."""
    global CONFIG_HIVE
    global ONLINE_HIVE
    config_dir = "config.yaml"
    if os.path.exists(os.path.join("resources", "config.yaml")):
        config_dir = os.path.join("resources", "config.yaml")
    with open(config_dir, "r") as f:
        global CONFIG_HIVE
        CONFIG_HIVE = yaml.safe_load(f.read())
    result = (
        gcloud_helper.sheets_service.spreadsheets()
        .values()
        .get(spreadsheetId=get("backend.configSheet"), range="A7:D8")
        .execute()
    ).get("values", [])
    for row in result:
        ONLINE_HIVE[row[0]] = (
            row[2]
            if row[2].lower() not in ("nothing", "", " ", "none")
            else row[3]
            if row[3] not in "NOTHING"
            else []
        )


def get(_i: str) -> any:
    """
    Get entry from the config file or environment variables.
    For example: ``general.token``

    :param _i: the configuration location identifier.
    :return: its value.
    """
    if CONFIG_HIVE == {}:
        init_config_hive()
    if _i in os.environ:
        if (
            "password" in _i
            or "token" in _i
            or "key" in _i
            or "email" in _i
            or "url" in _i
        ):
            logutils.debug(f"   ---> {len(os.environ[_i])*'*'}")
        else:
            logutils.debug(f"   ---> {os.environ[_i]}")
        return os.environ[_i]
    if _i.replace(".", "_") in os.environ:
        if (
            "password" in _i
            or "token" in _i
            or "key" in _i
            or "email" in _i
            or "url" in _i
        ):
            logutils.debug(f"   ---> {len(os.environ[_i.replace('.', '_')])*'*'}")
        else:
            logutils.debug(f"   ---> {os.environ[_i.replace('.', '_')]}")
        return os.environ[_i.replace(".", "_")]
    path = _i.split(".")
    if path[0] == "online":
        return ONLINE_HIVE[".".join(path[1:])]
    a = CONFIG_HIVE["config"].copy()
    try:
        for i in path:
            a = a[i]
        logutils.debug(f"   ---> {a}")
        return None if a == "None" else a
    except KeyError:
        logutils.error(f"Config entry `{_i}` not found.")
        return None


def read(_i):
    """
    Get entry from the config file or environment variables.
    For example: general.token.
    An alias for ``cfgman.get()``

    :param _i: the configuration location identifier.
    :return: its value.
    """
    return get(_i)
