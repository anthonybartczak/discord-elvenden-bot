import random
from typing import Dict, List, Optional

import discord

from config import ERROR_COLOR, INVITE_URL, MAIN_COLOR, SUCCESS_COLOR
import content.pictures as pic
from core.data import find_talent
from utils.formatters import build_blessing_embed, build_talent_embed
from utils.helpers import create_embed


class FortuneCardView(discord.ui.View):
    """Interactive card choice view for /fortuna command."""

    def __init__(
        self,
        author: discord.User | discord.Member,
        client_user: Optional[discord.ClientUser] = None
    ):
        super().__init__(timeout=45.0)
        self.author = author
        self.client_user = client_user
        self.winner_index = random.randint(0, 3)
        self.message: Optional[discord.Message] = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                "Tylko osoba, która poprosiła Ranalda o pomoc, może wybrać kartę!",
                ephemeral=True
            )
            return False
        return True

    async def handle_card_choice(self, interaction: discord.Interaction, card_index: int):
        # Disable all buttons upon selection
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True

        if card_index == self.winner_index:
            win_card_url = pic.WIN_CARDS[card_index]
            embed = create_embed(
                title="🤞 Twój wybór...",
                description=f"Świetnie {self.author.mention}, dziś Ranald wysłuchał Twej prośby!",
                color=SUCCESS_COLOR,
                image_url=win_card_url,
                client_user=self.client_user
            )
        else:
            lose_card_url = pic.LOSE_CARDS[card_index]
            winning_card_number = self.winner_index + 1
            embed = create_embed(
                title="🤞 Twój wybór...",
                description=(
                    f"{self.author.mention}, to był bardzo zły wybór...\n\n"
                    f"Szczęśliwą kartą była **karta nr {winning_card_number}**."
                ),
                color=ERROR_COLOR,
                image_url=lose_card_url,
                client_user=self.client_user
            )

        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

    @discord.ui.button(label="", emoji="1️⃣", style=discord.ButtonStyle.secondary)
    async def card_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_card_choice(interaction, 0)

    @discord.ui.button(label="", emoji="2️⃣", style=discord.ButtonStyle.secondary)
    async def card_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_card_choice(interaction, 1)

    @discord.ui.button(label="", emoji="3️⃣", style=discord.ButtonStyle.secondary)
    async def card_3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_card_choice(interaction, 2)

    @discord.ui.button(label="", emoji="4️⃣", style=discord.ButtonStyle.secondary)
    async def card_4(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_card_choice(interaction, 3)

    async def on_timeout(self):
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True

        if self.message:
            timeout_embed = create_embed(
                title="Za późno...",
                description=f"{self.author.mention}, Twój czas na wybór karty minął.",
                color=ERROR_COLOR,
                client_user=self.client_user
            )
            try:
                await self.message.edit(embed=timeout_embed, view=self)
            except discord.HTTPException:
                pass


class InviteView(discord.ui.View):
    """Button linking to the bot's invite authorization."""

    def __init__(self):
        super().__init__()
        self.add_item(
            discord.ui.Button(
                label="Zaproś bota na serwer",
                url=INVITE_URL,
                style=discord.ButtonStyle.link,
                emoji="🔗"
            )
        )


class TalentSelect(discord.ui.Select):
    """Select menu for inspecting related talents of an ability."""

    def __init__(self, talents: List[str], client_user: Optional[discord.ClientUser] = None):
        options = [
            discord.SelectOption(
                label=t[:100],
                value=t[:100],
                emoji="⚡",
                description=f"Zobacz szczegóły talentu {t}"[:100]
            )
            for t in talents[:25]
        ]
        super().__init__(
            placeholder="🔍 Zobacz opis powiązanego talentu...",
            min_values=1,
            max_values=1,
            options=options
        )
        self.client_user = client_user

    async def callback(self, interaction: discord.Interaction):
        selected_talent_name = self.values[0]
        talent_data = find_talent(selected_talent_name)

        if talent_data:
            embed = build_talent_embed(
                talent_data=talent_data,
                talent_name_fallback=selected_talent_name,
                client_user=self.client_user
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(
                f"⚠️ Nie udało się odnaleźć szczegółów dla talentu `{selected_talent_name}`.",
                ephemeral=True
            )


class TalentSelectView(discord.ui.View):
    """Interactive view containing a dropdown to inspect related talents."""

    def __init__(self, talents: List[str], client_user: Optional[discord.ClientUser] = None):
        super().__init__(timeout=180.0)
        if talents:
            self.add_item(TalentSelect(talents=talents, client_user=client_user))


class BlessingSelect(discord.ui.Select):
    """Select menu for inspecting specific blessings of a deity."""

    def __init__(
        self,
        blessings_list: List[str],
        cult_clean: str,
        cult_clean_names: Dict[str, str],
        cults_map: Dict[str, List[str]],
        blessings_map: Dict[str, dict],
        sl_bonuses_text: str = "",
        client_user: Optional[discord.ClientUser] = None
    ):
        self.cult_clean = cult_clean
        self.cult_clean_names = cult_clean_names
        self.cults_map = cults_map
        self.blessings_map = blessings_map
        self.sl_bonuses_text = sl_bonuses_text
        self.client_user = client_user

        options = []
        for b_key in blessings_list[:25]:
            b_data = blessings_map.get(b_key, {})
            b_name = b_data.get("name", b_key.capitalize())
            options.append(
                discord.SelectOption(
                    label=b_name[:100],
                    value=b_key,
                    emoji="✨",
                    description=f"Statystyki: {b_name}"[:100]
                )
            )

        super().__init__(
            placeholder="✨ Zobacz szczegóły wybranego błogosławieństwa...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        b_key = self.values[0]
        b_data = self.blessings_map.get(b_key)
        if b_data:
            cult_list = [
                self.cult_clean_names.get(c, c.capitalize())
                for c, bl in self.cults_map.items()
                if b_key in bl
            ]
            cults_str = ", ".join(cult_list) if cult_list else "Brak powiązanych kultów"
            embed = build_blessing_embed(
                blessing_data=b_data,
                blessing_name_fallback=b_key.capitalize(),
                matched_cult_clean=self.cult_clean,
                cults_str=cults_str,
                sl_bonuses_text=self.sl_bonuses_text,
                client_user=self.client_user
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(
                f"⚠️ Nie udało się odnaleźć szczegółów dla błogosławieństwa `{b_key}`.",
                ephemeral=True
            )


class BlessingSelectView(discord.ui.View):
    """Interactive view containing a dropdown of blessings for a deity."""

    def __init__(
        self,
        blessings_list: List[str],
        cult_clean: str,
        cult_clean_names: Dict[str, str],
        cults_map: Dict[str, List[str]],
        blessings_map: Dict[str, dict],
        sl_bonuses_text: str = "",
        client_user: Optional[discord.ClientUser] = None
    ):
        super().__init__(timeout=180.0)
        if blessings_list:
            self.add_item(
                BlessingSelect(
                    blessings_list=blessings_list,
                    cult_clean=cult_clean,
                    cult_clean_names=cult_clean_names,
                    cults_map=cults_map,
                    blessings_map=blessings_map,
                    sl_bonuses_text=sl_bonuses_text,
                    client_user=client_user
                )
            )


class HelpCategoryView(discord.ui.View):
    """Interactive category selector for the /pomoc help command."""

    def __init__(self, client_user: Optional[discord.ClientUser] = None):
        super().__init__(timeout=120.0)
        self.client_user = client_user

    def get_compendium_embed(self) -> discord.Embed:
        embed = create_embed(
            title="📚 Kompendium WFRP 4e",
            description="Polecenia służące do szybkiego wyszukiwania informacji w trakcie rozgrywki:",
            color=MAIN_COLOR,
            client_user=self.client_user
        )
        embed.add_field(
            name="⚡ `/talent <nazwa>`",
            value="Wyświetla pełny opis, testy oraz maksymalną wartość danego talentu.",
            inline=False
        )
        embed.add_field(
            name="📖 `/umiejętność <nazwa>`",
            value="Wyświetla opis, typ, cechę bazową oraz interaktywną listę powiązanych talentów.",
            inline=False
        )
        embed.add_field(
            name="✨ `/błogosławieństwo <bóstwo*> <nazwa*>`",
            value="Lista błogosławieństw dla danego kultu lub szczegółowe statystyki wybranego błogosławieństwa.",
            inline=False
        )
        return embed

    def get_mechanics_embed(self) -> discord.Embed:
        embed = create_embed(
            title="🎲 Mechanika gry WFRP 4e",
            description="Polecenia ułatwiające rozliczanie zasad i losowanie tabel:",
            color=MAIN_COLOR,
            client_user=self.client_user
        )
        embed.add_field(
            name="📊 `/rozwinięcie <cecha/umiejętność> <start> <cel> <talent*>`",
            value="Oblicza koszt rozwoju cechy lub umiejętności w punktach doświadczenia (PD).",
            inline=False
        )
        embed.add_field(
            name="📜 `/tabela_rozwinięć <wersja>`",
            value="Wyświetla tabelę *Koszt rozwoju cech i umiejętności w PD* (tekstowo lub graficznie).",
            inline=False
        )
        embed.add_field(
            name="⚡ `/manifestacja <mniejsza/większa>`",
            value="Losuje efekt mniejszej lub większej manifestacji magii z tabeli WFRP 4e (k100).",
            inline=False
        )
        embed.add_field(
            name="☣️ `/spaczenie <fizyczne/psychiczne>`",
            value="Losuje spaczenie fizyczne lub zepsucie psychiczne z tabeli WFRP 4e (k100).",
            inline=False
        )
        embed.add_field(
            name="🤞 `/fortuna`",
            value="Interaktywny wybór karty Ranalda przy użyciu Punktu Szczęścia.",
            inline=False
        )
        return embed

    def get_general_embed(self) -> discord.Embed:
        embed = create_embed(
            title="⚙️ Informacje i narzędzia",
            description="Ogólne informacje o bocie Elvie i zarządzaniu nim:",
            color=MAIN_COLOR,
            client_user=self.client_user
        )
        embed.add_field(
            name="❓ `/pomoc`",
            value="Wyświetla to interaktywne menu pomocy.",
            inline=False
        )
        embed.add_field(
            name="🌐 `/serwery`",
            value="Sprawdza liczbę połączonych serwerów Discord.",
            inline=False
        )
        embed.add_field(
            name="🔗 `/zaproszenie`",
            value="Generuje link z uprawnieniami do zaproszenia bota na Twój serwer.",
            inline=False
        )
        return embed

    def get_all_embed(self) -> discord.Embed:
        embed = create_embed(
            title="📖 Instrukcja bota Elvie (WFRP 4e)",
            description=(
                "Witaj! Elvie to asystent sesji **Warhammer Fantasy Roleplay 4. edycji**.\n"
                "Użyj poniższych przycisków, aby przeglądać poszczególne kategorie poleceń:\n\n"
                "• 📚 **Kompendium** – talenty, umiejętności, błogosławieństwa\n"
                "• 🎲 **Mechanika** – kalkulator PD, manifestacje, spaczenia, fortuna\n"
                "• ⚙️ **Informacje** – serwery, link zaproszenia, pomoc"
            ),
            color=MAIN_COLOR,
            client_user=self.client_user
        )
        return embed

    @discord.ui.button(label="Wszystko", emoji="🏠", style=discord.ButtonStyle.primary)
    async def btn_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=self.get_all_embed(), view=self)

    @discord.ui.button(label="Kompendium", emoji="📚", style=discord.ButtonStyle.secondary)
    async def btn_compendium(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=self.get_compendium_embed(), view=self)

    @discord.ui.button(label="Mechanika", emoji="🎲", style=discord.ButtonStyle.secondary)
    async def btn_mechanics(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=self.get_mechanics_embed(), view=self)

    @discord.ui.button(label="Informacje", emoji="⚙️", style=discord.ButtonStyle.secondary)
    async def btn_general(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=self.get_general_embed(), view=self)
