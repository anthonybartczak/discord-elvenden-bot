import discord
from discord import app_commands
from discord.ext import commands

from config import MAIN_COLOR
from utils.helpers import create_embed
from utils.views import InviteView


class GeneralCog(commands.Cog):
    """General utility commands (help, server count, invite)."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="serwery", description="Sprawdź do ilu serwerów jest połączony Elvie.")
    async def servers(self, interaction: discord.Interaction):
        guild_count = len(self.bot.guilds)
        description = f"Połączony z **{guild_count}** {'serwerem' if guild_count == 1 else 'serwerami'}.\n\n"
        embed = create_embed(
            title="Lista serwerów",
            description=description,
            color=MAIN_COLOR,
            client_user=self.bot.user
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pomoc", description="Pokazuje instrukcję bota Elvie.")
    async def help_command(self, interaction: discord.Interaction):
        description = (
            "Poniżej znajdziesz listę obecnie dostępnych poleceń slash. Argumenty oznaczone `*` są opcjonalne:\n\n"
            "**`/rozwinięcie <cecha/umiejętność> <start> <cel> <talent*>`**\n"
            "Oblicz koszt rozwoju od `start` do `cel` cechy lub umiejętności. Wybór talentu obniża koszt każdego rozwinięcia o 5 PD.\n\n"
            "**`/tabela_rozwinięć <wersja>`**\n"
            "Wyświetl tabelę *Koszt rozwoju cech i umiejętności w PD* (tekstowo lub w wersji graficznej).\n\n"
            "**`/talent <nazwa>`**\n"
            "Wyświetl opis, testy oraz maksymalną wartość danego talentu.\n\n"
            "**`/umiejętność <nazwa>`**\n"
            "Wyświetl opis, cechę bazową oraz powiązane talenty danej umiejętności.\n\n"
            "**`/błogosławieństwo <bóstwo*> <nazwa*>`**\n"
            "Wyświetl błogosławieństwa dla wybranego bóstwa lub szczegółowe statystyki konkretnego błogosławieństwa.\n\n"
            "**`/manifestacja <mniejsza/większa>`**\n"
            "Wylosuj mniejszą lub większą manifestację magii z tabeli WFRP 4e.\n\n"
            "**`/spaczenie <fizyczne/psychiczne>`**\n"
            "Wylosuj spaczenie fizyczne lub zepsucie psychiczne z tabeli WFRP 4e.\n\n"
            "**`/fortuna`**\n"
            "Wylosuj 4 zakryte karty i sprawdź, czy Ranald wysłucha Twej prośby!\n\n"
            "**`/zaproszenie`**\n"
            "Wygeneruj link zaproszenia, dzięki któremu dodasz bota na własny serwer.\n"
        )
        embed = create_embed(
            title="Krótka instrukcja bota Elvie",
            description=description,
            color=MAIN_COLOR,
            client_user=self.bot.user
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="zaproszenie", description="Wygeneruj zaproszenie dla bota Elvie.")
    async def invite(self, interaction: discord.Interaction):
        embed = create_embed(
            title="Link do zaproszenia",
            description="Kliknij poniższy przycisk, aby dodać Elviego do swojego serwera Discord:",
            color=MAIN_COLOR,
            client_user=self.bot.user
        )
        await interaction.response.send_message(embed=embed, view=InviteView())


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GeneralCog(bot))
