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

import datetime
import json

from . import time


def handle_time(t: str) -> datetime.datetime:
    """
    Convert a time string to a datetime object.

    Args:
        t (str): The time string.

    Returns:
        datetime: The datetime object converted.
    """
    timer = {"y": 0, "d": 0, "h": 0, "m": 0, "s": 0, "M": 0}

    buffer = ""
    for i in t:
        if i.isnumeric():
            buffer += str(i)
        elif i == "h":
            timer["h"] = int(buffer)
            buffer = ""
        elif i == "m":
            timer["m"] = int(buffer)
            buffer = ""
        elif i == "M":
            timer["M"] = int(buffer)
            buffer = ""
        elif i == "s":
            timer["s"] = int(buffer)
            buffer = ""
        elif i == "d":
            timer["d"] = int(buffer)
            buffer = ""
        elif i == "y":
            timer["y"] = int(buffer)
            buffer = ""

    dur = datetime.timedelta(
        seconds=timer["s"], minutes=timer["m"], hours=timer["h"], days=timer["d"]
    )
    a = datetime.datetime.now() + dur
    if timer["y"] == 0 and timer["M"] == 0:
        return a
    else:
        return datetime.datetime(
            year=a.year + timer["y"],
            second=timer["s"],
            minute=timer["m"],
            hour=timer["h"],
            day=timer["d"],
            month=timer["M"],
        )


def get_key(dictionary: dict, value: any):
    """
    A simple function to find a dict key by its value.

    Args:
        dictionary (dict): The dictionary to find the key in.
        value (any): The key's value.

    Returns:
        int | bool | str: The key.
    """
    for k, val in dictionary.items():
        if val == value:
            return k


def normalize_argument(value: str):
    try:
        arg = value.lower()
    except AttributeError:
        return None
    if arg in [
        "yes",
        "true",
        "yeah",
        "ok",
        "on",
        "y",
        "t",
        "1",
        "affirmative",
        "+",
        "có",
        "c",
        "positive",
    ]:
        return True
    elif arg in [
        "no",
        "false",
        "nope",
        "sike",
        "no",
        "off",
        "f",
        "n",
        "k",
        "không",
        "negative",
        "-",
        "0",
        "nah",
        "fuck",
    ]:
        return False
    elif arg in [
        "null",
        "none",
        "undefined",
        "không xác định",
        "\\0",
        "na",
        "unavailable",
    ]:
        return None
    elif '"' in arg:
        return value
    elif arg.replace(".", "").isnumeric():
        return float(value)
    elif arg.isnumeric():
        return int(value)
    elif "," in arg:
        return json.dumps(value)
    else:
        raise ValueError(f"Invalid argument given to normalize: {value}")


def str_in_str(str1: list, str2: str):
    for i in str1:
        if i in str2:
            return True
    else:
        return False
