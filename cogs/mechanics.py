import random

import discord
from discord import app_commands
from discord.ext import commands

from config import ERROR_COLOR, MAIN_COLOR
import content.pictures as pic
import content.tables as tab
from utils.helpers import create_embed
from utils.views import FortuneCardView


class MechanicsCog(commands.Cog):
    """WFRP 4e core game mechanics commands (advances, tables, miscasts, corruptions, fortune)."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="rozwinięcie", description="Oblicz koszt rozwinięcia cechy lub umiejętności w PD.")
    @app_commands.describe(
        choice="Co chcesz rozwinąć (cecha czy umiejętność)",
        init="Aktualna wartość rozwinięcia (np. 0, 5, 10)",
        goal="Docelowa wartość rozwinięcia (np. 15, 20)",
        talent="Czy posiadasz talent obniżający koszt o 5 PD za poziom?"
    )
    @app_commands.choices(
        choice=[
            app_commands.Choice(name="Cechy", value="cechy"),
            app_commands.Choice(name="Umiejętności", value="umiejętności"),
        ],
        talent=[
            app_commands.Choice(name="Tak (-5 PD)", value="tak"),
            app_commands.Choice(name="Nie", value="nie"),
        ]
    )
    async def advance(
        self,
        interaction: discord.Interaction,
        choice: str,
        init: int,
        goal: int,
        talent: str = "nie"
    ):
        if init < 0 or goal < 0:
            embed = create_embed(
                title="Błąd wartości",
                description="Wartości poziomu rozwinięcia nie mogą być ujemne.",
                color=ERROR_COLOR,
                client_user=self.bot.user
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if goal <= init:
            embed = create_embed(
                title="Błąd wartości",
                description=f"Wartość docelowa ({goal}) musi być większa od początkowej ({init}).",
                color=ERROR_COLOR,
                client_user=self.bot.user
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        ability_map = {
            5: 10, 10: 15, 15: 20, 20: 30, 25: 40, 30: 60,
            35: 80, 40: 110, 45: 140, 50: 180, 55: 220, 60: 270,
            65: 320, 70: 380, 99999: 440
        }
        attribute_map = {
            5: 25, 10: 30, 15: 40, 20: 50, 25: 70, 30: 90,
            35: 120, 40: 150, 45: 190, 50: 230, 55: 280, 60: 330,
            65: 390, 70: 450, 99999: 520
        }

        chosen_map = attribute_map if choice == "cechy" else ability_map

        current = init
        cost_sum = 0
        dif = goal - init

        for bracket_max, step_cost in chosen_map.items():
            while current < bracket_max and dif > 0:
                cost_sum += step_cost
                current += 1
                dif -= 1
            if dif == 0:
                break

        total_steps = goal - init
        description = (
            f"Początkowa wartość **{choice}**: **{init}**\n"
            f"Docelowa wartość **{choice}**: **{goal}** (Rozwinięcia: **+{total_steps}**)\n\n"
        )

        if talent == "tak":
            discount = 5 * total_steps
            final_cost = max(0, cost_sum - discount)
            description += (
                f"Talent obniża koszt o **5 PD** za każde rozwinięcie (łącznie -{discount} PD).\n\n"
                f"Finalny koszt rozwinięcia: **{final_cost} PD**"
            )
        else:
            description += f"Koszt rozwinięcia: **{cost_sum} PD**"

        embed = create_embed(
            title=f"Rozwinięcie {choice}",
            description=description,
            color=MAIN_COLOR,
            client_user=self.bot.user
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="manifestacja", description="Wylosuj mniejszą lub większą manifestację.")
    @app_commands.choices(
        choice=[
            app_commands.Choice(name="Mniejsza manifestacja", value="mniejsza"),
            app_commands.Choice(name="Większa manifestacja", value="większa"),
        ]
    )
    async def miscast(self, interaction: discord.Interaction, choice: str):
        roll = random.randint(1, 100)
        table = tab.MISCAST_MAJOR if choice == "większa" else tab.MISCAST_MINOR

        # Tables have 20 entries corresponding to 1-5, 6-10, ..., 96-100
        index = min((roll - 1) // 5, len(table) - 1)
        result_text = table[index]

        embed = create_embed(
            title=f"{choice.capitalize()} manifestacja!",
            description=f"Wyrzuciłeś **{roll}** na kościach k100:\n\n{result_text}",
            color=MAIN_COLOR,
            client_user=self.bot.user
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="spaczenie", description="Wylosuj spaczenie fizyczne lub zepsucie psychiczne.")
    @app_commands.choices(
        choice=[
            app_commands.Choice(name="Zepsucie psychiczne", value="zepsucie psychiczne"),
            app_commands.Choice(name="Spaczenie fizyczne", value="spaczenie fizyczne"),
        ]
    )
    async def corruption(self, interaction: discord.Interaction, choice: str):
        roll = random.randint(1, 100)
        table = tab.CORRUPTION_MENTAL if choice == "zepsucie psychiczne" else tab.CORRUPTION_PHYSICAL

        index = min((roll - 1) // 5, len(table) - 1)
        result_text = table[index]

        embed = create_embed(
            title=f"Wylosowano {choice}!",
            description=f"Wyrzuciłeś **{roll}** na kościach k100:\n\n{result_text}",
            color=MAIN_COLOR,
            client_user=self.bot.user
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="fortuna", description="Wylosuj kartę i sprawdź czy Ranald przygląda się Twoim losom!")
    async def fortune(self, interaction: discord.Interaction):
        embed = create_embed(
            title="Punkt szczęścia użyty!",
            description=(
                "Czyli Twoja dobra passa się skończyła i nagle chcesz, by sam **Ranald** Ci dopomógł?\n\n"
                "Dobrze, wybierz jedną z poniższych 4 kart, śmiertelniku..."
            ),
            color=MAIN_COLOR,
            image_url=pic.CARD_REVERSE,
            client_user=self.bot.user
        )
        view = FortuneCardView(author=interaction.user, client_user=self.bot.user)
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()

    @app_commands.command(name="tabela_rozwinięć", description="Wyświetl tabelę rozwinięcia cech lub umiejętności.")
    @app_commands.choices(
        version=[
            app_commands.Choice(name="Wersja tekstowa (PC)", value="PC"),
            app_commands.Choice(name="Wersja graficzna (mobilna)", value="mobilna"),
        ]
    )
    async def advance_table(self, interaction: discord.Interaction, version: str):
        if version == "mobilna":
            embed = create_embed(
                title="Koszt rozwoju cech i umiejętności w PD",
                description="",
                color=MAIN_COLOR,
                image_url=pic.ADVANCE_TABLE_PIC,
                client_user=self.bot.user
            )
        else:
            embed = create_embed(
                title="Koszt rozwoju cech i umiejętności w PD",
                description=tab.ADV_TABLE,
                color=MAIN_COLOR,
                client_user=self.bot.user
            )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MechanicsCog(bot))
