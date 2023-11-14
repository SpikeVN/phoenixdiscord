import disnake
import numpy
from disnake.ext import commands

import configuration as cfg
import i18n
import logutils
import utils


async def handle_command(cmd: disnake.Message, guild: disnake.Guild):
    c = cmd.content.split(" ")
    del c[0]
    if len(c) != 4 and c[0].lower() in ["reverse-damage", "rd", "revdmg"]:
        return
    del c[0]
    if c[0].lower() in ["md", "massdel", "mass-delete"]:
        if c[1].lower() in ["channel", "cn", "c"]:
            if cmd.author.top_role.permissions.manage_channels():
                await cmd.reply(
                    f"Deleting every channel with name containing {c[2]}..."
                )
                for i in guild.channels:
                    if c[2] in i.name and i.id != cmd.channel.id:
                        await i.delete(reason="Admin-requested operation.")
                await cmd.channel.send("Done!")


class AntiRaid(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.guild is None:
            return
        if (
            not cfg.get("modules.antiRaid.enable")
            or message.guild.id not in cfg.get("modules.antiRaid.guilds")
            or message.author.id == self.bot.user.id
        ):
            return
        if self.bot.user.mention in message.content:
            await handle_command(message, message.guild)
            return
        c = message.content
        a = message.author
        logutils.debug(f"Checking spamming content for message with authour {a}")
        mass_ping = "@everyone" in c or "@here" in c
        if mass_ping:
            print("User is mass pinging.")
        is_raid = 0
        if mass_ping:
            if a.bot and a.id:
                is_raid += 1
                logutils.debug("    -> A bot. Isolating...")
            elif not a.top_role.permissions.moderate_members:
                logutils.debug("    -> Not an admin.")
                is_raid += 0.2
        if utils.str_in_str([".com", ".net", ".gift", ".gg", "http", "//"], c):
            is_raid += 0.3
            logutils.debug("The message has link.")

        i18n_list = message.channel.history(limit=5)
        author_list = []
        times = []
        async for i in i18n_list:
            author_list.append(i.author.id)
            times.append(i.created_at.timestamp())
        print(author_list)
        if author_list.count(author_list[0]) == len(author_list) != 0:
            is_raid += 0.3
            logutils.debug(
                f"owner sends message repeatedly. {author_list}, {numpy.average(numpy.abs(numpy.diff(times)))}"
            )
            avg_time = numpy.average(numpy.abs(numpy.diff(times)))
            if avg_time < 2:
                is_raid += 0.2
                logutils.debug("time check not pass.")

        sus_action = []
        async for entry in message.guild.audit_logs(limit=5):
            sus_action.append(entry.changes.after)

        is_raid = is_raid >= cfg.get("modules.antiRaid.spamThreshold")
        if is_raid:
            logutils.debug("Taking actions")
            if message.webhook_id:
                # Very clever.
                wh = await self.bot.fetch_webhook(message.webhook_id)
                m = await message.guild.fetch_member(wh.user.id)
                await m.kick(reason="Participating in raid.")
                await wh.delete(reason="Participating in raid.")
            else:
                if a in message.guild.members:
                    await a.kick()
                    card = disnake.Embed(
                        title=i18n.translated_string(
                            "antiRaid.susTitle", i18n.Locale.VIETNAMESE
                        )
                    )
                    card.add_field(
                        i18n.translated_string(
                            "intel.card.name", i18n.Locale.VIETNAMESE
                        ),
                        a.name,
                    )
                    card.add_field(
                        i18n.translated_string(
                            "antiRaid.action", i18n.Locale.VIETNAMESE
                        ),
                        i18n.get(i18n.Locale.VIETNAMESE, "antiRaid.isolateMember"),
                    )
                    await message.channel.send(embed=card)


def setup(bot):
    bot.add_cog(AntiRaid(bot))
