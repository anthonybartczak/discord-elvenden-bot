import discord
from discord import app_commands
from discord.ext import commands

from config import MAIN_COLOR
from utils.helpers import create_embed
from utils.views import HelpCategoryView, InviteView


class GeneralCog(commands.Cog):
    """General utility commands (help, server count, invite)."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="serwery", description="Sprawdź do ilu serwerów jest połączony Elvie.")
    async def servers(self, interaction: discord.Interaction):
        guild_count = len(self.bot.guilds)
        server_word = "serwerem" if guild_count == 1 else "serwerami"
        embed = create_embed(
            title="🌐 Połączone serwery",
            description=f"Elvie aktualnie wspiera graczy na **{guild_count}** {server_word}.",
            color=MAIN_COLOR,
            client_user=self.bot.user
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pomoc", description="Pokazuje instrukcję bota Elvie.")
    async def help_command(self, interaction: discord.Interaction):
        view = HelpCategoryView(client_user=self.bot.user)
        embed = view.get_all_embed()
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="zaproszenie", description="Wygeneruj zaproszenie dla bota Elvie.")
    async def invite(self, interaction: discord.Interaction):
        embed = create_embed(
            title="🔗 Zaproszenie bota",
            description=(
                "Kliknij poniższy przycisk, aby dodać **Elviego** do swojego serwera Discord "
                "i korzystać z szybkiego kompendium WFRP 4e:"
            ),
            color=MAIN_COLOR,
            client_user=self.bot.user
        )
        await interaction.response.send_message(embed=embed, view=InviteView())


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GeneralCog(bot))
