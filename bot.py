import asyncio
import json
import logging
import os
from pathlib import Path
import random
import unicodedata
from typing import List, Optional

import discord
from discord import app_commands
from dotenv import load_dotenv

import content.pictures as pic
import content.tables as tab

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("elvie-bot")

# Main colors used for the bot's embedded messages formatting
MAIN_COLOR = 0x8B54CF
ERROR_COLOR = 0xFF0000
SUCCESS_COLOR = 0x16BD00

# Bot token and configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
INVITE_URL = (
    "https://discord.com/api/oauth2/authorize?"
    "client_id=864205486056669244&permissions=1084516330561&scope=bot%20applications.commands"
)

# Footer text (version + update info)
FOOTER_TEXT = "Elvie v1.1.0 - WFRP 4ED"

# Base directory for reliable relative file access
BASE_DIR = Path(__file__).resolve().parent
CONTENT_DIR = BASE_DIR / "content"

with open(CONTENT_DIR / "talents.json", "r", encoding="utf-8") as jf:
    TALENTS_DATA: dict[str, dict] = json.load(jf)

with open(CONTENT_DIR / "abilities.json", "r", encoding="utf-8") as jf:
    ABILITIES_DATA: dict[str, dict] = json.load(jf)

with open(CONTENT_DIR / "blessings.json", "r", encoding="utf-8") as jf:
    BLESSINGS_DATA: dict[str, dict] = json.load(jf)

BLESSINGS_MAP: dict[str, dict] = BLESSINGS_DATA.get("blessings", {})
CULTS_MAP: dict[str, list[str]] = BLESSINGS_DATA.get("cults", {})
SL_BONUSES: list[dict] = BLESSINGS_DATA.get("sl_bonuses", [])

CULT_DISPLAY_NAMES: dict[str, str] = {
    "manann": "Manann (Bóg Mórz i Oceanów)",
    "morr": "Morr (Bóg Śmierci i Snów)",
    "myrmidia": "Myrmidia (Bogini Sztuki Wojennej i Strategii)",
    "ranald": "Ranald (Bóg Złodziei i Hazardu)",
    "rhya": "Rhya (Bogini Ziemi, Płodności i Wiosny)",
    "shallya": "Shallya (Bogini Miłosierdzia i Uzdrawiania)",
    "sigmar": "Sigmar (Patron Imperium)",
    "taal": "Taal (Bóg Natury, Dziczy i Zwierząt)",
    "ulryk": "Ulryk (Bóg Wojny, Zimy i Wilków)",
    "verena": "Verena (Bogini Mądrości i Sprawiedliwości)",
}

SL_BONUSES_TEXT = (
    "Każde **+2 PS** pozwala wybrać jeden z bonusów:\n"
    "• **Zasięg:** +6 metrów\n"
    "• **Liczba celów:** +1\n"
    "• **Czas trwania:** +6 rund *(niedostępne dla efektów natychmiastowych)*"
)


POLISH_CHAR_MAP = str.maketrans({
    "ł": "l", "Ł": "l",
    "ą": "a", "ć": "c", "ę": "e", "ń": "n", "ó": "o", "ś": "s", "ź": "z", "ż": "z",
    "Ą": "a", "Ć": "c", "Ę": "e", "Ń": "n", "Ó": "o", "Ś": "s", "Ź": "z", "Ż": "z"
})


def normalize_text(text: str) -> str:
    """Normalize text for fuzzy search: lowercase, stripped accents, strokes, and symbols."""
    translated = text.translate(POLISH_CHAR_MAP).lower()
    nfkd = unicodedata.normalize("NFKD", translated)
    stripped = "".join(c for c in nfkd if not unicodedata.combining(c))
    return stripped.replace("_", " ").replace("-", " ").strip()


# ---------------------------
# PRECOMPUTED LOOKUPS & ALIASES
# ---------------------------

CULT_CLEAN_NAMES: dict[str, str] = {
    k: CULT_DISPLAY_NAMES.get(k, k).split(" (")[0] for k in CULTS_MAP
}

BLESSING_SHORT_NAMES: dict[str, str] = {
    k: v.get("name", k).replace("Błogosławieństwo ", "").strip() for k, v in BLESSINGS_MAP.items()
}

PRECOMPUTED_CULTS = [
    {
        "key": k,
        "display_name": disp,
        "clean_name": CULT_CLEAN_NAMES.get(k, k),
        "norm_key": normalize_text(k),
        "norm_display": normalize_text(disp),
        "norm_clean": normalize_text(CULT_CLEAN_NAMES.get(k, k)),
    }
    for k in CULTS_MAP
    for disp in [CULT_DISPLAY_NAMES.get(k, k)]
]

PRECOMPUTED_BLESSINGS = [
    {
        "key": k,
        "name": raw_name,
        "short_name": BLESSING_SHORT_NAMES.get(k, raw_name),
        "norm_key": normalize_text(k),
        "norm_name": normalize_text(raw_name),
        "norm_short": normalize_text(BLESSING_SHORT_NAMES.get(k, raw_name)),
    }
    for k, v in BLESSINGS_MAP.items()
    for raw_name in [v.get("name", k)]
]

PRECOMPUTED_TALENTS = [
    {
        "key": k,
        "name": data.get("name", k),
        "norm_key": normalize_text(k),
        "norm_name": normalize_text(data.get("name", k)),
    }
    for k, data in TALENTS_DATA.items()
]

PRECOMPUTED_ABILITIES = [
    {
        "key": k,
        "name": data.get("name", k),
        "norm_key": normalize_text(k),
        "norm_name": normalize_text(data.get("name", k)),
    }
    for k, data in ABILITIES_DATA.items()
]


def create_embed(
    title: str,
    description: str,
    color: int = MAIN_COLOR,
    image_url: Optional[str] = None,
    client_user: Optional[discord.ClientUser] = None
) -> discord.Embed:
    """Helper to create standardized embeds across all commands."""
    embed = discord.Embed(title=title, description=description, color=color)
    icon_url = client_user.display_avatar.url if client_user else pic.BOT_AVATAR
    embed.set_footer(text=FOOTER_TEXT, icon_url=icon_url)
    if image_url:
        embed.set_image(url=image_url)
    return embed


class FortuneCardView(discord.ui.View):
    """Interactive card choice view for /fortuna command."""

    def __init__(self, author: discord.User | discord.Member, client_user: Optional[discord.ClientUser] = None):
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


class ElvieBot(discord.Client):
    """Custom Discord Client with CommandTree synchronization."""

    def __init__(self) -> None:
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        logger.info("Synchronizowanie drzewa poleceń slash...")
        await self.tree.sync()
        logger.info("Drzewo poleceń zsynchronizowane pomyślnie.")

    async def on_ready(self) -> None:
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(name="/pomoc | WFRP 4e")
        )
        logger.info("Zalogowano jako %s (ID: %s)", self.user, self.user.id if self.user else "N/A")


client = ElvieBot()
tree = client.tree


# ---------------------------
# SLASH COMMANDS
# ---------------------------

@tree.command(name="serwery", description="Sprawdź do ilu serwerów jest połączony Elvie.")
async def servers(interaction: discord.Interaction):
    guild_count = len(client.guilds)
    description = f"Połączony z **{guild_count}** {'serwerem' if guild_count == 1 else 'serwerami'}.\n\n"
    embed = create_embed(
        title="Lista serwerów",
        description=description,
        color=MAIN_COLOR,
        client_user=client.user
    )
    await interaction.response.send_message(embed=embed)


@tree.command(name="pomoc", description="Pokazuje instrukcję bota Elvie.")
async def help_command(interaction: discord.Interaction):
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
        client_user=client.user
    )
    await interaction.response.send_message(embed=embed)


@tree.command(name="zaproszenie", description="Wygeneruj zaproszenie dla bota Elvie.")
async def invite(interaction: discord.Interaction):
    embed = create_embed(
        title="Link do zaproszenia",
        description="Kliknij poniższy przycisk, aby dodać Elviego do swojego serwera Discord:",
        color=MAIN_COLOR,
        client_user=client.user
    )
    await interaction.response.send_message(embed=embed, view=InviteView())


@tree.command(name="rozwinięcie", description="Oblicz koszt rozwinięcia cechy lub umiejętności w PD.")
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
            client_user=client.user
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if goal <= init:
        embed = create_embed(
            title="Błąd wartości",
            description=f"Wartość docelowa ({goal}) musi być większa od początkowej ({init}).",
            color=ERROR_COLOR,
            client_user=client.user
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
        client_user=client.user
    )
    await interaction.response.send_message(embed=embed)


@tree.command(name="manifestacja", description="Wylosuj mniejszą lub większą manifestację.")
@app_commands.choices(
    choice=[
        app_commands.Choice(name="Mniejsza manifestacja", value="mniejsza"),
        app_commands.Choice(name="Większa manifestacja", value="większa"),
    ]
)
async def miscast(interaction: discord.Interaction, choice: str):
    roll = random.randint(1, 100)
    table = tab.MISCAST_MAJOR if choice == "większa" else tab.MISCAST_MINOR

    # Tables have 20 entries corresponding to 1-5, 6-10, ..., 96-100
    index = min((roll - 1) // 5, len(table) - 1)
    result_text = table[index]

    embed = create_embed(
        title=f"{choice.capitalize()} manifestacja!",
        description=f"Wyrzuciłeś **{roll}** na kościach k100:\n\n{result_text}",
        color=MAIN_COLOR,
        client_user=client.user
    )
    await interaction.response.send_message(embed=embed)


@tree.command(name="spaczenie", description="Wylosuj spaczenie fizyczne lub zepsucie psychiczne.")
@app_commands.choices(
    choice=[
        app_commands.Choice(name="Zepsucie psychiczne", value="zepsucie psychiczne"),
        app_commands.Choice(name="Spaczenie fizyczne", value="spaczenie fizyczne"),
    ]
)
async def corruption(interaction: discord.Interaction, choice: str):
    roll = random.randint(1, 100)
    table = tab.CORRUPTION_MENTAL if choice == "zepsucie psychiczne" else tab.CORRUPTION_PHYSICAL

    index = min((roll - 1) // 5, len(table) - 1)
    result_text = table[index]

    embed = create_embed(
        title=f"Wylosowano {choice}!",
        description=f"Wyrzuciłeś **{roll}** na kościach k100:\n\n{result_text}",
        color=MAIN_COLOR,
        client_user=client.user
    )
    await interaction.response.send_message(embed=embed)


@tree.command(name="fortuna", description="Wylosuj kartę i sprawdź czy Ranald przygląda się Twoim losom!")
async def fortune(interaction: discord.Interaction):
    embed = create_embed(
        title="Punkt szczęścia użyty!",
        description=(
            "Czyli Twoja dobra passa się skończyła i nagle chcesz, by sam **Ranald** Ci dopomógł?\n\n"
            "Dobrze, wybierz jedną z poniższych 4 kart, śmiertelniku..."
        ),
        color=MAIN_COLOR,
        image_url=pic.CARD_REVERSE,
        client_user=client.user
    )
    view = FortuneCardView(author=interaction.user, client_user=client.user)
    await interaction.response.send_message(embed=embed, view=view)
    view.message = await interaction.original_response()


@tree.command(name="tabela_rozwinięć", description="Wyświetl tabelę rozwinięcia cech lub umiejętności.")
@app_commands.choices(
    version=[
        app_commands.Choice(name="Wersja tekstowa (PC)", value="PC"),
        app_commands.Choice(name="Wersja graficzna (mobilna)", value="mobilna"),
    ]
)
async def advance_table(interaction: discord.Interaction, version: str):
    if version == "mobilna":
        embed = create_embed(
            title="Koszt rozwoju cech i umiejętności w PD",
            description="",
            color=MAIN_COLOR,
            image_url=pic.ADVANCE_TABLE_PIC,
            client_user=client.user
        )
    else:
        embed = create_embed(
            title="Koszt rozwoju cech i umiejętności w PD",
            description=tab.ADV_TABLE,
            color=MAIN_COLOR,
            client_user=client.user
        )
    await interaction.response.send_message(embed=embed)


@tree.command(name="talent", description="Wyświetl opis i szczegóły talentu.")
@app_commands.describe(talent_name="Nazwa szukanego talentu")
async def talent(interaction: discord.Interaction, talent_name: str):
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
            client_user=client.user
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
            client_user=client.user
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


@talent.autocomplete("talent_name")
async def talent_autocomplete(
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


@tree.command(name="umiejętność", description="Wyświetl opis i szczegóły umiejętności.")
@app_commands.describe(ability_name="Nazwa szukanej umiejętności")
async def ability(interaction: discord.Interaction, ability_name: str):
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
            client_user=client.user
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
            client_user=client.user
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


@ability.autocomplete("ability_name")
async def ability_autocomplete(
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


def find_cult(query: str) -> Optional[str]:
    """Find cult key matching query (by key, full display name, deity name, or stem)."""
    q = normalize_text(query)
    for c in PRECOMPUTED_CULTS:
        if q == c["norm_key"] or q == c["norm_display"] or q == c["norm_clean"]:
            return c["key"]
    for c in PRECOMPUTED_CULTS:
        if (q in c["norm_key"] or q in c["norm_display"] or q in c["norm_clean"] or
            c["norm_key"] in q or c["norm_clean"] in q):
            return c["key"]
    for c in PRECOMPUTED_CULTS:
        if len(q) >= 3 and (q[:4] == c["norm_key"][:4] or c["norm_key"][:4] in q):
            return c["key"]
    return None


def find_blessing(query: str) -> Optional[str]:
    """Find blessing key matching query (by key, full name, short name, or stem)."""
    q = normalize_text(query)
    q_clean = q.replace("blogoslawienstwo", "").strip() or q
    for b in PRECOMPUTED_BLESSINGS:
        if (q == b["norm_key"] or 
            q == b["norm_name"] or 
            q == b["norm_short"] or
            q_clean == b["norm_key"] or
            q_clean == b["norm_short"]):
            return b["key"]
    for b in PRECOMPUTED_BLESSINGS:
        if (q in b["norm_key"] or q in b["norm_name"] or q in b["norm_short"] or
            q_clean in b["norm_key"] or q_clean in b["norm_short"] or
            b["norm_key"] in q or b["norm_short"] in q or b["norm_key"] in q_clean or b["norm_short"] in q_clean):
            return b["key"]
    for b in PRECOMPUTED_BLESSINGS:
        if len(q_clean) >= 4 and (q_clean[:4] == b["norm_key"][:4] or q_clean[:4] == b["norm_short"][:4]):
            return b["key"]
    return None


async def handle_blessing_command(
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
            client_user=client.user
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
            client_user=client.user
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
            client_user=client.user
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
            client_user=client.user
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
        client_user=client.user
    )
    overview_lines = []
    for k, blist in CULTS_MAP.items():
        cult_name = CULT_CLEAN_NAMES.get(k, k)
        names = [BLESSING_SHORT_NAMES.get(b, b) for b in blist]
        overview_lines.append(f"• **{cult_name}**: {', '.join(names)}")

    embed.add_field(name="Kulty", value="\n".join(overview_lines), inline=False)
    embed.add_field(name="💫 Bonusy za Poziomy Sukcesu (+2 PS)", value=SL_BONUSES_TEXT, inline=False)
    await interaction.response.send_message(embed=embed)


async def cult_autocomplete(
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


async def blessing_autocomplete(
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


@tree.command(name="błogosławieństwo", description="Wyświetl błogosławieństwa bóstw lub szczegóły wybranego błogosławieństwa.")
@app_commands.describe(
    bóstwo="Wybierz bóstwo/kult (np. Sigmar, Ulryk, Shallya)",
    nazwa="Nazwa konkretnego błogosławieństwa (np. Bitwy, Uzdrawiania)"
)
@app_commands.autocomplete(bóstwo=cult_autocomplete, nazwa=blessing_autocomplete)
async def blessing(
    interaction: discord.Interaction,
    bóstwo: Optional[str] = None,
    nazwa: Optional[str] = None
):
    await handle_blessing_command(interaction, god_name=bóstwo, blessing_name=nazwa)


# ---------------------------
# MAIN EXECUTION
# ---------------------------

if __name__ == "__main__":
    if not BOT_TOKEN:
        logger.error("Błąd: Brak zmiennej BOT_TOKEN w pliku .env!")
        exit(1)

    client.run(BOT_TOKEN)