import disnake
from disnake.ext import commands

import configuration as cfg
import database
import i18n
import logutils
import utils
from modules.moderation.commands import enough_permission

LANGUAGE = i18n.Locale.ENGLISH


async def autocomp_langs(_: disnake.ApplicationCommandInteraction, user_input: str):
    return [
        f"{langcode} : {langname}"
        for langname, langcode in i18n.AVALIABLE_LOCALES.items()
        if user_input.lower() in langname.lower()
        or user_input.lower() in langcode.lower()
    ]


class LanguageChooser(disnake.ui.Select):
    def __init__(self):
        super().__init__()

        for lan, lanid in i18n.AVALIABLE_LOCALES.items():
            self.add_option(label=lan, value=lanid)

    async def callback(self, interaction: disnake.MessageInteraction):
        usr = database.User(interaction.author)
        usr.locale = i18n.get_locale(self.values[0])
        await interaction.send(
            i18n.translated_string(
                "commands.setup.languageSuccess", i18n.get_locale(self.values[0])
            ).replace("{lang}", utils.get_key(i18n.AVALIABLE_LOCALES, self.values[0]))
        )


class DontSpamMeButton(disnake.ui.Button):
    def __init__(self):
        super().__init__(
            label=i18n.translated_string("commands.setup.noDM", i18n.Locale.VIETNAMESE),
            style=disnake.ButtonStyle.red,
        )

    async def callback(self, interaction: disnake.MessageInteraction):
        await interaction.send(
            i18n.translated_string("commands.setup.noDMok", interaction.locale)
        )
        database.User(interaction.author).disable_direct_message()


class Setup(commands.Cog):
    """
    Task that runs when player joins
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(
        name="settings", description="Internal Admin-only invocation."
    )
    async def settings(self, inter):
        pass

    @settings.sub_command(
        name="language",
        description="Language settings. Will be in English in case of accidental misconfiguration.",
    )
    async def settings_language(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        language: str = commands.Param(
            name="language",
            description="The language to set to",
            autocomplete=autocomp_langs,
        ),
    ):
        usr = database.User(interaction.author)
        usr.locale = i18n.get_locale(language.split()[0])
        await interaction.send(
            i18n.translated_string("commands.setup.languageSuccess", usr.locale)
        )

    @commands.slash_command(name="setuplang", description="Admin Internal Command")
    async def setuplang(self, interaction: disnake.ApplicationCommandInteraction):
        global LANGUAGE
        LANGUAGE = interaction.locale
        if not await enough_permission(interaction):
            return
        ui = disnake.ui.View()
        ui.add_item(LanguageChooser())
        ui.add_item(DontSpamMeButton())
        await interaction.send(
            i18n.translated_string("commands.setup.card", interaction.locale), view=ui
        )
        database.User(interaction.author)

    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member):
        global LANGUAGE
        LANGUAGE = "em"
        if member.bot:
            return
        logutils.info(
            f"{member} ({member.id}) has joined the server. Executing jointask..."
        )
        ui = disnake.ui.View()
        ui.add_item(LanguageChooser())
        ui.add_item(DontSpamMeButton())
        await member.send(
            i18n.translated_string("commands.setup.card", i18n.Locale.VIETNAMESE),
            view=ui,
        )
        await member.add_roles(
            member.guild.get_role(int(cfg.get("general.defaultRoleID")))
        )
        database.User(member)


def setup(bot: commands.Bot):
    bot.add_cog(Setup(bot))
