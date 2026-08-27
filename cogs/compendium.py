from typing import List, Optional

import discord
from discord import app_commands
from discord.ext import commands

from config import ERROR_COLOR, MAIN_COLOR
from core.data import (
    ABILITIES_DATA,
    BLESSING_SHORT_NAMES,
    BLESSINGS_MAP,
    CULT_CLEAN_NAMES,
    CULT_DISPLAY_NAMES,
    CULTS_MAP,
    PRECOMPUTED_ABILITIES,
    PRECOMPUTED_BLESSINGS,
    PRECOMPUTED_CULTS,
    PRECOMPUTED_TALENTS,
    SL_BONUSES_TEXT,
    TALENTS_DATA,
    find_blessing,
    find_cult,
)
from utils.helpers import create_embed, normalize_text


class CompendiumCog(commands.Cog):
    """WFRP 4e compendium lookup commands (talents, skills/abilities, blessings)."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="talent", description="Wyświetl opis i szczegóły talentu.")
    @app_commands.describe(talent_name="Nazwa szukanego talentu")
    async def talent(self, interaction: discord.Interaction, talent_name: str):
        key = talent_name.strip().lower().replace(" ", "_")
        talent_data = TALENTS_DATA.get(key)

        # If exact key not found, fallback to normalized search
        if not talent_data:
            normalized_target = normalize_text(talent_name)
            for t in PRECOMPUTED_TALENTS:
                if t["norm_key"] == normalized_target or t["norm_name"] == normalized_target:
                    talent_data = TALENTS_DATA.get(t["key"])
                    break

        if talent_data:
            embed = create_embed(
                title=talent_data.get("name", talent_name),
                description=talent_data.get("description", "Brak opisu."),
                color=MAIN_COLOR,
                client_user=self.bot.user
            )
            embed.add_field(name="Maksimum", value=talent_data.get("max", "N/A"), inline=True)
            embed.add_field(name="Testy", value=talent_data.get("tests", "N/A"), inline=True)
            await interaction.response.send_message(embed=embed)
        else:
            embed = create_embed(
                title="⚠️ Nie znaleziono talentu",
                description=(
                    f"Nie znaleziono talentu o nazwie `{talent_name}`.\n"
                    "Użyj autouzupełniania podczas wpisywania, aby wybrać właściwą nazwę."
                ),
                color=ERROR_COLOR,
                client_user=self.bot.user
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @talent.autocomplete("talent_name")
    async def talent_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ) -> List[app_commands.Choice[str]]:
        query = normalize_text(current)
        choices: List[app_commands.Choice[str]] = []

        for t in PRECOMPUTED_TALENTS:
            if not query or query in t["norm_name"] or query in t["norm_key"]:
                choices.append(app_commands.Choice(name=t["name"][:100], value=t["key"]))
                if len(choices) >= 25:
                    break

        return choices

    @app_commands.command(name="umiejętność", description="Wyświetl opis i szczegóły umiejętności.")
    @app_commands.describe(ability_name="Nazwa szukanej umiejętności")
    async def ability(self, interaction: discord.Interaction, ability_name: str):
        key = ability_name.strip().lower().replace(" ", "_")
        ability_data = ABILITIES_DATA.get(key)

        if not ability_data:
            normalized_target = normalize_text(ability_name)
            for a in PRECOMPUTED_ABILITIES:
                if a["norm_key"] == normalized_target or a["norm_name"] == normalized_target:
                    ability_data = ABILITIES_DATA.get(a["key"])
                    break

        if ability_data:
            embed = create_embed(
                title=ability_data.get("name", ability_name),
                description=ability_data.get("description", "Brak opisu."),
                color=MAIN_COLOR,
                client_user=self.bot.user
            )
            embed.add_field(name="Typ", value=ability_data.get("type", "N/A"), inline=False)
            embed.add_field(name="Cecha", value=ability_data.get("attribute", "N/A"), inline=False)
            embed.add_field(name="Talenty", value=ability_data.get("talents", "Brak"), inline=False)
            await interaction.response.send_message(embed=embed)
        else:
            embed = create_embed(
                title="⚠️ Nie znaleziono umiejętności",
                description=(
                    f"Nie znaleziono umiejętności o nazwie `{ability_name}`.\n"
                    "Użyj autouzupełniania podczas wpisywania, aby wybrać właściwą nazwę."
                ),
                color=ERROR_COLOR,
                client_user=self.bot.user
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @ability.autocomplete("ability_name")
    async def ability_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ) -> List[app_commands.Choice[str]]:
        query = normalize_text(current)
        choices: List[app_commands.Choice[str]] = []

        for a in PRECOMPUTED_ABILITIES:
            if not query or query in a["norm_name"] or query in a["norm_key"]:
                choices.append(app_commands.Choice(name=a["name"][:100], value=a["key"]))
                if len(choices) >= 25:
                    break

        return choices

    async def _handle_blessing_command(
        self,
        interaction: discord.Interaction,
        god_name: Optional[str] = None,
        blessing_name: Optional[str] = None
    ):
        """Core logic to display deity blessings, specific blessing info, or an overview."""
        matched_cult = find_cult(god_name) if god_name else None
        matched_blessing = find_blessing(blessing_name) if blessing_name else None

        # Error handling when user provided arguments that weren't found
        if god_name and not matched_cult:
            embed = create_embed(
                title="⚠️ Nie znaleziono bóstwa",
                description=(
                    f"Nie znaleziono bóstwa o nazwie `{god_name}`.\n\n"
                    "**Dostępne bóstwa:** Manann, Morr, Myrmidia, Ranald, Rhya, Shallya, Sigmar, Taal, Ulryk, Verena.\n"
                    "Użyj autouzupełniania podczas wpisywania, aby wybrać właściwą nazwę."
                ),
                color=ERROR_COLOR,
                client_user=self.bot.user
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if blessing_name and not matched_blessing:
            embed = create_embed(
                title="⚠️ Nie znaleziono błogosławieństwa",
                description=(
                    f"Nie znaleziono błogosławieństwa o nazwie `{blessing_name}`.\n"
                    "Użyj autouzupełniania podczas wpisywania, aby wybrać właściwą nazwę."
                ),
                color=ERROR_COLOR,
                client_user=self.bot.user
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Specific blessing requested (or both god and blessing specified)
        if matched_blessing:
            b_data = BLESSINGS_MAP[matched_blessing]
            b_name = b_data.get("name", matched_blessing.capitalize())
            cult_list = [
                CULT_CLEAN_NAMES.get(c, c.capitalize())
                for c, bl in CULTS_MAP.items()
                if matched_blessing in bl
            ]
            cults_str = ", ".join(cult_list) if cult_list else "Brak powiązanych kultów"

            desc = "Szczegółowe parametry błogosławieństwa (WFRP 4e):"
            if matched_cult:
                cult_name = CULT_CLEAN_NAMES.get(matched_cult, matched_cult)
                if matched_blessing in CULTS_MAP.get(matched_cult, []):
                    desc = f"Błogosławieństwo dostępne w kulcie bóstwa **{cult_name}**:"
                else:
                    desc = f"⚠️ Bóstwo **{cult_name}** nie posiada tego błogosławieństwa (jest ono dostępne dla: **{cults_str}**)."

            embed = create_embed(
                title=f"✨ {b_name}",
                description=desc,
                color=MAIN_COLOR,
                client_user=self.bot.user
            )
            embed.add_field(name="Zasięg", value=str(b_data.get("range", "–")), inline=True)
            embed.add_field(name="Liczba celów", value=str(b_data.get("targets", "–")), inline=True)
            embed.add_field(name="Czas trwania", value=str(b_data.get("duration", "–")), inline=True)
            embed.add_field(name="Efekt", value=b_data.get("effect", "–"), inline=False)
            embed.add_field(name="Dostępne dla bóstw", value=cults_str, inline=False)
            embed.add_field(name="💫 Bonusy za Poziomy Sukcesu (+2 PS)", value=SL_BONUSES_TEXT, inline=False)
            await interaction.response.send_message(embed=embed)
            return

        # Deity blessings requested
        if matched_cult:
            cult_display = CULT_DISPLAY_NAMES.get(matched_cult, matched_cult.capitalize())
            cult_name = CULT_CLEAN_NAMES.get(matched_cult, matched_cult.capitalize())
            blessings_list = CULTS_MAP[matched_cult]

            embed = create_embed(
                title=f"✨ Błogosławieństwa: {cult_display}",
                description=f"Bóstwo **{cult_name}** obdarza swoich wyznawców 6 następującymi błogosławieństwami:\n",
                color=MAIN_COLOR,
                client_user=self.bot.user
            )
            for b_key in blessings_list:
                b_data = BLESSINGS_MAP.get(b_key, {})
                b_name = b_data.get("name", b_key.capitalize())
                b_range = b_data.get("range", "–")
                b_targets = b_data.get("targets", "–")
                b_dur = b_data.get("duration", "–")
                b_eff = b_data.get("effect", "–")
                embed.add_field(
                    name=f"🌟 {b_name}",
                    value=(
                        f"**Zasięg:** {b_range} | **Cel:** {b_targets} | **Czas:** {b_dur}\n"
                        f"**Efekt:** {b_eff}"
                    ),
                    inline=False
                )
            embed.add_field(
                name="💫 Bonusy za Poziomy Sukcesu (+2 PS)",
                value=SL_BONUSES_TEXT,
                inline=False
            )
            await interaction.response.send_message(embed=embed)
            return

        # Overview of all cults
        embed = create_embed(
            title="✨ Błogosławieństwa bóstw (WFRP 4e)",
            description=(
                "W WFRP 4e kapłani oraz wtajemniczeni mogą prosić swoich bogów o zesłanie błogosławieństw "
                "(**Test Modlitwy** oparty na **Charyzmie**).\n\n"
                "Aby sprawdzić szczegóły, wpisz:\n"
                "• `/błogosławieństwo bóstwo:<nazwa>` — lista 6 błogosławieństw danego bóstwa\n"
                "• `/błogosławieństwo nazwa:<nazwa>` — statystyki i opis konkretnego błogosławieństwa\n\n"
                "**Bóstwa i przypisane im błogosławieństwa:**"
            ),
            color=MAIN_COLOR,
            client_user=self.bot.user
        )
        overview_lines = []
        for k, blist in CULTS_MAP.items():
            cult_name = CULT_CLEAN_NAMES.get(k, k)
            names = [BLESSING_SHORT_NAMES.get(b, b) for b in blist]
            overview_lines.append(f"• **{cult_name}**: {', '.join(names)}")

        embed.add_field(name="Kulty", value="\n".join(overview_lines), inline=False)
        embed.add_field(name="💫 Bonusy za Poziomy Sukcesu (+2 PS)", value=SL_BONUSES_TEXT, inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="błogosławieństwo",
        description="Wyświetl błogosławieństwa bóstw lub szczegóły wybranego błogosławieństwa."
    )
    @app_commands.describe(
        bóstwo="Wybierz bóstwo/kult (np. Sigmar, Ulryk, Shallya)",
        nazwa="Nazwa konkretnego błogosławieństwa (np. Bitwy, Uzdrawiania)"
    )
    async def blessing(
        self,
        interaction: discord.Interaction,
        bóstwo: Optional[str] = None,
        nazwa: Optional[str] = None
    ):
        await self._handle_blessing_command(interaction, god_name=bóstwo, blessing_name=nazwa)

    @blessing.autocomplete("bóstwo")
    async def cult_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ) -> List[app_commands.Choice[str]]:
        query = normalize_text(current)
        choices: List[app_commands.Choice[str]] = []

        for c in PRECOMPUTED_CULTS:
            if not query or query in c["norm_key"] or query in c["norm_display"] or query in c["norm_clean"]:
                choices.append(app_commands.Choice(name=c["display_name"][:100], value=c["key"]))
                if len(choices) >= 25:
                    break

        return choices

    @blessing.autocomplete("nazwa")
    async def blessing_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ) -> List[app_commands.Choice[str]]:
        query = normalize_text(current)
        q_clean = query.replace("blogoslawienstwo", "").strip() or query
        choices: List[app_commands.Choice[str]] = []

        for b in PRECOMPUTED_BLESSINGS:
            if (not query or 
                query in b["norm_name"] or 
                query in b["norm_key"] or 
                query in b["norm_short"] or
                q_clean in b["norm_name"] or
                q_clean in b["norm_short"]):
                choices.append(app_commands.Choice(name=b["name"][:100], value=b["key"]))
                if len(choices) >= 25:
                    break

        return choices


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CompendiumCog(bot))
