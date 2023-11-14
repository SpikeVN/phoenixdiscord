import random
from typing import Callable

import disnake

import configuration as cfg
import gcloud_helper

COMMANDS: dict[str, Callable] = {}


async def handle(m: disnake.Message):
    al = m.content.split()
    if al[0][1:] in COMMANDS:
        await COMMANDS[al[0][1:]](m, al[1:])


def update_commands():
    result = (
        gcloud_helper.sheets_service.spreadsheets()
        .values()
        .get(spreadsheetId=cfg.get("backend.configSheet"), range="13:32")
        .execute()
    ).get("values", [])
    for row in result:
        if len(row) > 1:

            def ccb():
                nrow = row.copy()

                async def cb(message: disnake.Message, args: list[str]) -> bool:
                    if len(nrow) == 2:
                        await message.reply(
                            "xác định lệnh lỗi: k định nghĩa câu trl. W bot, L human"
                        )
                        return True
                    if len(args) != 0:
                        tok = {}
                        for i, t in enumerate(nrow[1].split()[1:]):
                            if t[0] == "%" and t[-1] == "%":
                                if t[1] == "*":
                                    tok[t[2:-1]] = args
                                else:
                                    tok[t[1:-1]] = args[i]
                        response = random.choice(nrow[2:])
                        if len(tok) != len(args):
                            await message.reply(
                                "số tham số trong template không trùng với tham số mà mày đút vào. you L bruh"
                            )
                            return True
                        for k, v in tok.items():
                            if isinstance(v, list):
                                response = response.replace(f"%*{k}%", " ".join(v))
                            else:
                                response = response.replace(f"%{k}%", v)
                        await message.reply(response.replace("\\n", "\n"))
                    else:
                        await message.reply(
                            random.choice(nrow[2:]).replace("\\n", "\n")
                        )
                    return True

                return cb

            try:
                COMMANDS[row[1].split()[0]] = ccb()
            except IndexError:
                pass
