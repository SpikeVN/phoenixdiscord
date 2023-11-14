import datetime

import disnake
from disnake.ext import commands

import configuration as cfg
import database
import gcloud_helper
import i18n
import security

EVENTS = {}
INVALIDATION = datetime.datetime.utcfromtimestamp(0)


class EventViewer(disnake.ui.Select):
    def __init__(self):
        super().__init__()

        for i, e in enumerate(EVENTS):
            self.add_option(label=e["summary"], value=i)

    async def callback(self, interaction: disnake.MessageInteraction):
        locale = database.User(interaction.author).locale
        choice = EVENTS[int(self.values[0])]
        embed = disnake.Embed()
        embed.title = choice.get("summary", "N/A")
        if "displayName" in choice["creator"]:
            embed.add_field(
                i18n.translated_string("commands.whatsup.extra.adder", locale),
                choice["creator"]["displayName"],
            )
        else:
            embed.add_field(
                i18n.translated_string("commands.whatsup.extra.adder", locale),
                choice["creator"].get("email", "N/A"),
            )
        embed.add_field(
            "Deadline",
            datetime.datetime.fromisoformat(choice["start"]["dateTime"]).strftime(
                i18n.translated_string("boilerplate.date", locale)
            ),
        )
        embed.footer.text = datetime.datetime.fromisoformat(choice["created"]).strftime(
            i18n.translated_string("boilerplate.date", locale)
        )

        embed.add_field(
            i18n.translated_string("commands.whatsup.extra.description", locale),
            choice.get("description", "N/A"),
        )

        await interaction.send(embed=embed)


def update_events():
    global EVENTS
    global INVALIDATION
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    events_result = (
        gcloud_helper.calendar_service.events()
        .list(
            calendarId=cfg.get("modules.gcal.calid"),
            timeMin=now,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    EVENTS = events_result.get("items", [])

    if not EVENTS:
        EVENTS = []


class Reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="whatsup", description=i18n.localized_command_description("whatsup")
    )
    async def whatsup(self, interaction: disnake.ApplicationCommandInteraction):
        await interaction.response.defer()
        if (
            EVENTS is None
            or datetime.datetime.now() - INVALIDATION > datetime.timedelta(minutes=1)
        ):
            update_events()
        ev_str = []
        for i, event in enumerate(EVENTS):
            start = datetime.datetime.fromisoformat(
                event["start"].get("dateTime", event["start"].get("date"))
            ) - datetime.datetime.now(
                tz=datetime.timezone(datetime.timedelta(hours=-7))
            )
            ev_str.append(
                f"{i + 1}.  +{f'{start.days}d ' if start.days != 0 else ''}{start.seconds / 60 / 60:.0f}h: {event['summary']}"
            )
        if len(ev_str) == 0:
            await interaction.edit_original_response(
                i18n.translated_string("commands.whatsup.nothing", interaction.author)
            )
        else:
            v = disnake.ui.View()
            v.add_item(EventViewer())
            await interaction.edit_original_response(
                security.safe_format(
                    i18n.translated_string(
                        "commands.whatsup.reportCard", interaction.author
                    ),
                    asn="```" + "\n".join(ev_str) + "```",
                ),
                view=v,
            )


def setup(bot: commands.Bot):
    bot.add_cog(Reminder(bot))
