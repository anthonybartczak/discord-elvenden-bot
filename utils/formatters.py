import random
import re
from typing import Dict, List, Optional, Tuple

import discord

from config import FOOTER_TEXT, MAIN_COLOR
import content.pictures as pic
import content.tables as tab

# Map of characteristic codes to full Polish names and representative emojis
ATTRIBUTE_MAP: Dict[str, str] = {
    "WW": "WW (Walka Wręcz)",
    "US": "US (Umiejętności Strzeleckie)",
    "S": "S (Siła)",
    "Wt": "Wt (Wytrzymałość)",
    "I": "I (Inicjatywa)",
    "Zw": "Zw (Zwinność)",
    "Zr": "Zr (Zręczność)",
    "Int": "Int (Inteligencja)",
    "SW": "SW (Siła Woli)",
    "Ogd": "Ogd (Ogłada)",
}

# Key WFRP terms to highlight in descriptions for fast scanning during gameplay
WFRP_RULES_KEYWORDS = [
    r"Test(?:u|em|ach|y)? Przeciwstawn(?:y|ego|ym|emu|e|ych)?",
    r"Wydłużon(?:y|ego|ym|emu|e|ych)? Test(?:u|em|ach|y)?",
    r"Test(?:u|em|ach|y)? Prost(?:y|ego|ym|emu|e|ych)?",
    r"Test(?:u|em|ach|y)? Zwykł(?:y|ego|ym|emu|e|ych)?",
    r"Wymagając(?:y|ego|ym|emu|e|a|ej|ą)? \(\+0\)",
    r"Przeciętn(?:y|ego|ym|emu|e|a|ej|ą)? \(\+20\)",
    r"Łatw(?:y|ego|ym|emu|e|a|ej|ą)? \(\+40\)",
    r"Bardzo Łatw(?:y|ego|ym|emu|e|a|ej|ą)? \(\+60\)",
    r"Trudn(?:y|ego|ym|emu|e|a|ej|ą)? \(\-20\)",
    r"Bardzo Trudn(?:y|ego|ym|emu|e|a|ej|ą)? \(\-30\)",
    r"Zdumiewając(?:a|ej|ą|y|ego|ym)? Porażk(?:a|i|ę|ą)",
    r"Zdumiewając(?:e|ego|ym)? Powodzeni(?:e|a|u)",
    r"Trafieni(?:e|a|em|u)? Krytyczn(?:e|ego|ym)?",
    r"Tabel(?:i|a|ę|ą) Trafień Krytycznych",
    r"Poziom(?:y|ów|em|ie|ach)? Sukcesu",
    r"\bPS\b",
    r"Przewag(?:a|i|ę|ą|o)",
    r"Punkt(?:y|ów|em|ach)? Bohatera",
    r"Punkt(?:y|ów|em|ach)? Determinacji",
    r"Punkt(?:y|ów|em|ach)? Szczęścia",
    r"Punkt(?:y|ów|em|ach)? Przeznaczenia",
    r"Punkt(?:y|ów|em|ach)? Zepsucia",
    r"Stan(?:u|em|ach|y)? Krwawieni(?:e|a|em)",
    r"Stan(?:u|em|ach|y)? Zmęczeni(?:e|a|em|ony)",
    r"Stan(?:u|em|ach|y)? Ogłuszeni(?:e|a|em)",
    r"Stan(?:u|em|ach|y)? Oślepieni(?:e|a|em)",
    r"Stan(?:u|em|ach|y)? Pochwyceni(?:e|a|em)",
    r"Stan(?:u|em|ach|y)? Panik(?:a|i|ę|ą)",
    r"Stan(?:u|em|ach|y)? Podpaleni(?:e|a|em)",
    r"Stan(?:u|em|ach|y)? Powaleni(?:e|a|em)",
    r"Stan(?:u|em|ach|y)? Oszołomieni(?:e|a|em)",
    r"Stan(?:u|em|ach|y)? Zaskoczon(?:y|ego|ym|i)",
    r"Szał(?:u|em)? Bojow(?:y|ego|ym)",
]


def format_wfrp_description(text: str) -> str:
    """Intelligently formats long WFRP rules texts with paragraph breaks, sections, and bolded keywords."""
    if not text or text.strip() == "Brak opisu.":
        return "Brak opisu."

    cleaned = text.strip()

    # Format bullet lists cleanly
    cleaned = re.sub(r"[ \t]*•[ \t]*", "\n• ", cleaned)
    cleaned = re.sub(r"(?:\r?\n•)", "\n•", cleaned)

    # Insert clean section breaks before key subsections if present in text
    cleaned = re.sub(
        r"(?<=[.!?])\s*(Przykładowe Specjalizacje:\s*)",
        r"\n\n**Przykładowe Specjalizacje:**\n",
        cleaned,
        flags=re.IGNORECASE
    )
    cleaned = re.sub(
        r"(?<=[.!?])\s*(Specjalizacje:\s*)",
        r"\n\n**Specjalizacje:**\n",
        cleaned,
        flags=re.IGNORECASE
    )
    cleaned = re.sub(
        r"(?<=[.!?])\s*(?:W walce:\s*|W walce\s+)",
        r"\n\n**W walce:** ",
        cleaned,
        flags=re.IGNORECASE
    )
    cleaned = re.sub(
        r"(?<=[.!?])\s*(Więcej informacji na ten temat znajduje się\b)",
        r"\n\n*Więcej informacji na ten temat znajduje się*",
        cleaned,
        flags=re.IGNORECASE
    )
    cleaned = re.sub(
        r"(?<=[.!?])\s*(Uwaga:\s*)",
        r"\n\n**Uwaga:** ",
        cleaned,
        flags=re.IGNORECASE
    )
    cleaned = re.sub(
        r"(?<=[.!?])\s*(Na przykład:\s*|Dla przykładu:\s*)",
        r"\n\n*Na przykład:* ",
        cleaned,
        flags=re.IGNORECASE
    )

    # Split into blocks by existing paragraph breaks
    raw_blocks = [b.strip() for b in cleaned.split("\n\n") if b.strip()]
    formatted_blocks = []

    for block in raw_blocks:
        # If block is a list or subsection header, preserve as is
        if block.startswith("•") or block.startswith("**") or "\n•" in block:
            formatted_blocks.append(block)
            continue

        sentences = re.split(r"(?<=[.!?])\s+", block)
        if len(sentences) <= 1:
            formatted_blocks.append(block)
            continue

        paragraphs = []
        curr_p = []
        curr_len = 0

        for s in sentences:
            # Trigger paragraph break when a sentence starts with mechanical / conditional rules or references
            is_rule_trigger = bool(re.match(
                r"^(Kiedy|Jeśli|Jeżeli|Gdy|Za każdym razem|W przypadku|Dodatkowo|Ponadto|Możesz|Musisz|MG|Testy|Każde|Każda|Każdy|Więcej|Wykorzystanie|Rozdział)\b",
                s,
                re.IGNORECASE
            ))

            if curr_p and (curr_len >= 120 or is_rule_trigger or len(curr_p) >= 2):
                paragraphs.append(" ".join(curr_p))
                curr_p = [s]
                curr_len = len(s)
            else:
                curr_p.append(s)
                curr_len += len(s)

        if curr_p:
            paragraphs.append(" ".join(curr_p))

        formatted_blocks.append("\n\n".join(paragraphs))

    cleaned = "\n\n".join(formatted_blocks)

    # Highlight rules keywords (avoid double bolding)
    for kw in WFRP_RULES_KEYWORDS:
        pattern = re.compile(rf"(?<!\*\*)\b({kw})\b(?!\*\*)", flags=re.IGNORECASE)
        cleaned = pattern.sub(r"**\1**", cleaned)

    return cleaned


def parse_talents_list(talents_raw: str) -> List[str]:
    """Parses a comma-separated list of talents into individual cleaned talent names."""
    if not talents_raw or talents_raw.strip() in ["N/A", "Brak", "brak", "-", "–"]:
        return []
    parts = [t.strip() for t in talents_raw.split(",") if t.strip()]
    return parts


def format_talents_display(talents: List[str]) -> str:
    """Formats a list of talents into cleanly spaced Discord backtick chips."""
    if not talents:
        return "*Brak powiązanych talentów*"
    if len(talents) <= 4:
        return " • ".join(f"`{t}`" for t in talents)
    # For longer lists, group neatly across lines (4 per line)
    chunks = [talents[i:i + 4] for i in range(0, len(talents), 4)]
    return "\n".join(" • ".join(f"`{t}`" for t in chunk) for chunk in chunks)


def build_talent_embed(
    talent_data: dict,
    talent_name_fallback: str = "Talent",
    client_user: Optional[discord.ClientUser] = None
) -> discord.Embed:
    """Builds a polished RPG card embed for a talent."""
    name = talent_data.get("name", talent_name_fallback)
    raw_desc = talent_data.get("description", "Brak opisu.")
    formatted_desc = format_wfrp_description(raw_desc)

    embed = discord.Embed(
        title=f"⚡ Talent: {name}",
        description=formatted_desc,
        color=MAIN_COLOR
    )

    max_val = talent_data.get("max", "N/A")
    tests_val = talent_data.get("tests", "N/A")

    embed.add_field(name="📈 Maksimum", value=f"**{max_val}**", inline=True)
    embed.add_field(name="🎲 Testy", value=f"**{tests_val}**", inline=True)

    icon_url = client_user.display_avatar.url if client_user else pic.BOT_AVATAR
    embed.set_footer(text=FOOTER_TEXT, icon_url=icon_url)
    return embed


def build_ability_embed(
    ability_data: dict,
    ability_name_fallback: str = "Umiejętność",
    client_user: Optional[discord.ClientUser] = None
) -> Tuple[discord.Embed, List[str]]:
    """Builds a polished RPG card embed for an ability/skill."""
    name = ability_data.get("name", ability_name_fallback)
    raw_desc = ability_data.get("description", "Brak opisu.")
    formatted_desc = format_wfrp_description(raw_desc)

    ab_type = ability_data.get("type", "Podstawowa")
    attr_code = ability_data.get("attribute", "N/A")
    formatted_attr = ATTRIBUTE_MAP.get(attr_code, attr_code)

    embed = discord.Embed(
        title=f"📖 Umiejętność: {name}",
        description=formatted_desc,
        color=MAIN_COLOR
    )

    # Top inline fields for instantaneous stat check
    embed.add_field(name="🏷️ Typ", value=f"**{ab_type}**", inline=True)
    embed.add_field(name="🎲 Cecha", value=f"**{formatted_attr}**", inline=True)

    raw_talents = ability_data.get("talents", "")
    talents_list = parse_talents_list(raw_talents)
    talents_str = format_talents_display(talents_list)

    count_suffix = f" ({len(talents_list)})" if talents_list else ""
    embed.add_field(name=f"✨ Powiązane talenty{count_suffix}", value=talents_str, inline=False)

    icon_url = client_user.display_avatar.url if client_user else pic.BOT_AVATAR
    embed.set_footer(text=FOOTER_TEXT, icon_url=icon_url)
    return embed, talents_list


def build_blessing_embed(
    blessing_data: dict,
    blessing_name_fallback: str = "Błogosławieństwo",
    matched_cult_clean: Optional[str] = None,
    cults_str: str = "",
    sl_bonuses_text: str = "",
    client_user: Optional[discord.ClientUser] = None
) -> discord.Embed:
    """Builds a detailed RPG card embed for a specific deity blessing."""
    b_name = blessing_data.get("name", blessing_name_fallback)

    if matched_cult_clean:
        if matched_cult_clean in cults_str:
            desc = f"Błogosławieństwo dostępne w kulcie bóstwa **{matched_cult_clean}**:"
        else:
            desc = f"⚠️ Bóstwo **{matched_cult_clean}** nie posiada tego błogosławieństwa (dostępne dla: **{cults_str}**)."
    else:
        desc = "Szczegółowe parametry błogosławieństwa (WFRP 4e):"

    embed = discord.Embed(
        title=f"✨ {b_name}",
        description=desc,
        color=MAIN_COLOR
    )

    embed.add_field(name="🎯 Zasięg", value=f"**{blessing_data.get('range', '–')}**", inline=True)
    embed.add_field(name="👥 Cel", value=f"**{blessing_data.get('targets', '–')}**", inline=True)
    embed.add_field(name="⏳ Czas trwania", value=f"**{blessing_data.get('duration', '–')}**", inline=True)

    effect_text = format_wfrp_description(blessing_data.get("effect", "–"))
    embed.add_field(name="📜 Efekt", value=effect_text, inline=False)
    embed.add_field(name="🏛️ Dostępne dla kultów", value=f"**{cults_str}**" if cults_str else "Brak", inline=False)
    if sl_bonuses_text:
        embed.add_field(name="💫 Bonusy za Poziomy Sukcesu (+2 PS)", value=sl_bonuses_text, inline=False)

    icon_url = client_user.display_avatar.url if client_user else pic.BOT_AVATAR
    embed.set_footer(text=FOOTER_TEXT, icon_url=icon_url)
    return embed


def build_cult_blessings_embed(
    cult_display: str,
    cult_clean: str,
    blessings_list: List[str],
    blessings_map: Dict[str, dict],
    sl_bonuses_text: str = "",
    client_user: Optional[discord.ClientUser] = None
) -> discord.Embed:
    """Builds an overview card embed of all 6 blessings for a deity."""
    embed = discord.Embed(
        title=f"✨ Błogosławieństwa: {cult_display}",
        description=(
            f"Bóstwo **{cult_clean}** obdarza swoich wyznawców 6 następującymi błogosławieństwami "
            f"(wymagany **Test Modlitwy** oparty na **Charyzmie**):\n"
        ),
        color=MAIN_COLOR
    )

    for b_key in blessings_list:
        b_data = blessings_map.get(b_key, {})
        b_name = b_data.get("name", b_key.capitalize())
        b_range = b_data.get("range", "–")
        b_targets = b_data.get("targets", "–")
        b_dur = b_data.get("duration", "–")
        b_eff = b_data.get("effect", "–")

        embed.add_field(
            name=f"🌟 {b_name}",
            value=(
                f"🎯 **Zasięg:** `{b_range}`  •  👥 **Cel:** `{b_targets}`  •  ⏳ **Czas:** `{b_dur}`\n\n"
                f"> {b_eff}"
            ),
            inline=False
        )

    if sl_bonuses_text:
        embed.add_field(name="💫 Bonusy za Poziomy Sukcesu (+2 PS)", value=sl_bonuses_text, inline=False)

    icon_url = client_user.display_avatar.url if client_user else pic.BOT_AVATAR
    embed.set_footer(text=FOOTER_TEXT, icon_url=icon_url)
    return embed


def build_advance_embed(
    choice: str,
    init: int,
    goal: int,
    total_steps: int,
    cost_sum: int,
    talent: str,
    discount: int,
    final_cost: int,
    client_user: Optional[discord.ClientUser] = None
) -> discord.Embed:
    """Builds a formatted advance cost calculation embed."""
    choice_label = choice.capitalize()
    embed = discord.Embed(
        title=f"📊 Rozwinięcie: {choice_label}",
        color=MAIN_COLOR
    )

    embed.add_field(
        name="🎯 Zakres rozwinięcia",
        value=f"**{init}** ➔ **{goal}** (`+{total_steps}` {choice})",
        inline=True
    )
    embed.add_field(name="🏷️ Kategoria", value=f"**{choice_label}**", inline=True)
    embed.add_field(name="💰 Koszt bazowy", value=f"**{cost_sum} PD**", inline=True)

    if talent == "tak":
        embed.add_field(name="🎖️ Zniżka (Talent)", value=f"**-{discount} PD** (-5 PD / krok)", inline=True)
        embed.add_field(name="💎 Koszt końcowy", value=f"**{final_cost} PD**", inline=True)
    else:
        embed.add_field(name="💎 Koszt całkowity", value=f"**{cost_sum} PD**", inline=True)

    icon_url = client_user.display_avatar.url if client_user else pic.BOT_AVATAR
    embed.set_footer(text=FOOTER_TEXT, icon_url=icon_url)
    return embed


def build_table_roll_embed(
    table_name: str,
    roll: int,
    result_raw: str,
    client_user: Optional[discord.ClientUser] = None
) -> discord.Embed:
    """Builds an embed for miscast/corruption random roll tables."""
    lines = result_raw.strip().split("\n", 1)
    title_line = lines[0].replace("*", "").strip()
    body_line = lines[1].strip() if len(lines) > 1 else ""

    formatted_body = format_wfrp_description(body_line)

    embed = discord.Embed(
        title=f"⚡ {table_name}",
        color=MAIN_COLOR
    )
    embed.add_field(name="🎲 Wynik rzutu", value=f"k100 = **{roll}**", inline=True)
    embed.add_field(name="🏷️ Wynik", value=f"**{title_line}**", inline=True)
    embed.add_field(name="📜 Opis efektu", value=formatted_body, inline=False)

    icon_url = client_user.display_avatar.url if client_user else pic.BOT_AVATAR
    embed.set_footer(text=FOOTER_TEXT, icon_url=icon_url)
    return embed


def format_years(n: int) -> str:
    """Format year count according to Polish grammatical rules."""
    if n == 1:
        return "1 rok"
    last_two = n % 100
    if 11 <= last_two <= 14:
        return f"{n} lat"
    last_digit = n % 10
    if last_digit in (2, 3, 4):
        return f"{n} lata"
    return f"{n} lat"


def generate_physiognomy(race_key: str = "losowa") -> dict:
    """
    Generate character physiognomy (age, height, eye color, hair color)
    based on WFRP 4e core rulebook tables.
    """
    valid_races = list(tab.PHYSIOGNOMY_RACES.keys())
    if race_key == "losowa" or race_key not in tab.PHYSIOGNOMY_RACES:
        race_key = random.choice(valid_races)

    race_info = tab.PHYSIOGNOMY_RACES[race_key]
    race_name = race_info["name"]
    emoji = race_info.get("emoji", "👤")

    # 1. Wiek (Age)
    age_base = race_info["age_base"]
    num_dice, die_faces = race_info["age_dice"]
    age_rolls = [random.randint(1, die_faces) for _ in range(num_dice)]
    age_dice_sum = sum(age_rolls)
    total_age = age_base + age_dice_sum

    if num_dice == 1:
        age_roll_str = f"`{age_base} + 1k10 [{age_rolls[0]}]`"
    elif num_dice <= 5:
        rolls_joined = " + ".join(str(r) for r in age_rolls)
        age_roll_str = f"`{age_base} + {num_dice}k{die_faces} [{rolls_joined} = {age_dice_sum}]`"
    else:
        age_roll_str = f"`{age_base} + {num_dice}k{die_faces} [suma: {age_dice_sum}]`"

    # 2. Wzrost (Height)
    height_base = race_info["height_base"]
    h_num_dice, h_die_faces = race_info["height_dice"]
    is_exploding = race_info.get("height_exploding", False)

    height_rolls_details = []
    height_dice_sum = 0

    if is_exploding:
        # Human exploding 10s rule
        for _ in range(h_num_dice):
            r = random.randint(1, 10)
            if r == 10:
                bonus_rolls = []
                curr_bonus = random.randint(1, 10)
                bonus_rolls.append(curr_bonus)
                while curr_bonus == 10:
                    curr_bonus = random.randint(1, 10)
                    bonus_rolls.append(curr_bonus)
                sub_sum = 10 + sum(bonus_rolls)
                height_dice_sum += sub_sum
                bonus_str = ", ".join(f"+{b}" for b in bonus_rolls)
                height_rolls_details.append(f"10 ({bonus_str})")
            else:
                height_dice_sum += r
                height_rolls_details.append(str(r))

        rolls_joined = ", ".join(height_rolls_details)
        total_height = height_base + height_dice_sum
        height_roll_str = f"`{height_base} + 4k10 [{rolls_joined} = {height_dice_sum}]`"
    else:
        h_rolls = [random.randint(1, h_die_faces) for _ in range(h_num_dice)]
        height_dice_sum = sum(h_rolls)
        total_height = height_base + height_dice_sum
        rolls_joined = " + ".join(str(r) for r in h_rolls)
        height_roll_str = f"`{height_base} + {h_num_dice}k{h_die_faces} [{rolls_joined} = {height_dice_sum}]`"

    # 3. Kolor Oczu (Eye Color)
    if race_key in ("wysoki_elf", "lesny_elf"):
        # Elves roll twice on 2k10
        r1_a, r1_b = random.randint(1, 10), random.randint(1, 10)
        r2_a, r2_b = random.randint(1, 10), random.randint(1, 10)
        roll1 = r1_a + r1_b
        roll2 = r2_a + r2_b
        color1 = tab.lookup_eye_color(race_key, roll1)
        color2 = tab.lookup_eye_color(race_key, roll2)

        if color1 == color2:
            eye_color_display = f"**{color1}** *(jednolite)*"
            eye_roll_str = f"2x 2k10: `[{r1_a}+{r1_b} = {roll1}]`, `[{r2_a}+{r2_b} = {roll2}]`"
        else:
            eye_color_display = f"**{color1}** oraz **{color2}** *(dwubarwne / nakrapiane)*"
            eye_roll_str = f"2x 2k10: `[{r1_a}+{r1_b} = {roll1} ➔ {color1}]`, `[{r2_a}+{r2_b} = {roll2} ➔ {color2}]`"
    else:
        r_a, r_b = random.randint(1, 10), random.randint(1, 10)
        roll = r_a + r_b
        color = tab.lookup_eye_color(race_key, roll)
        eye_color_display = f"**{color}**"
        eye_roll_str = f"2k10: `[{r_a}+{r_b} = {roll}]`"

    # 4. Kolor Włosów (Hair Color)
    hr_a, hr_b = random.randint(1, 10), random.randint(1, 10)
    hair_roll = hr_a + hr_b
    hair_color = tab.lookup_hair_color(race_key, hair_roll)
    hair_color_display = f"**{hair_color}**"
    hair_roll_str = f"2k10: `[{hr_a}+{hr_b} = {hair_roll}]`"

    return {
        "race_key": race_key,
        "race_name": race_name,
        "emoji": emoji,
        "age": total_age,
        "age_roll_str": age_roll_str,
        "age_avg": race_info["age_avg"],
        "height": total_height,
        "height_roll_str": height_roll_str,
        "height_avg": race_info["height_avg"],
        "eye_color_display": eye_color_display,
        "eye_roll_str": eye_roll_str,
        "hair_color_display": hair_color_display,
        "hair_roll_str": hair_roll_str,
        "notes": race_info["notes"],
    }


def build_physiognomy_embed(
    physio_data: dict,
    client_user: Optional[discord.ClientUser] = None
) -> discord.Embed:
    """Builds a clean, elegant RPG character physiognomy sheet embed."""
    race_name = physio_data["race_name"]
    emoji = physio_data.get("emoji", "👤")

    embed = discord.Embed(
        title=f"{emoji} Fizjonomia postaci: {race_name}",
        description="Wylosowane cechy wyglądu i budowy ciała na podstawie oficjalnych tabel **WFRP 4e**:",
        color=MAIN_COLOR
    )

    embed.add_field(
        name="⏳ Wiek",
        value=(
            f"**{format_years(physio_data['age'])}**\n"
            f"Rzut: {physio_data['age_roll_str']}\n"
            f"*Średnia życia: {physio_data['age_avg']}*"
        ),
        inline=False
    )

    embed.add_field(
        name="📏 Wzrost",
        value=(
            f"**{physio_data['height']} cm**\n"
            f"Rzut: {physio_data['height_roll_str']}\n"
            f"*Średni wzrost: {physio_data['height_avg']}*"
        ),
        inline=False
    )

    embed.add_field(
        name="👁️ Kolor oczu",
        value=(
            f"{physio_data['eye_color_display']}\n"
            f"Rzut: {physio_data['eye_roll_str']}"
        ),
        inline=False
    )

    embed.add_field(
        name="💇 Kolor włosów",
        value=(
            f"{physio_data['hair_color_display']}\n"
            f"Rzut: {physio_data['hair_roll_str']}"
        ),
        inline=False
    )

    if physio_data.get("notes"):
        embed.add_field(
            name="📜 Cechy szczególne i wygląd",
            value=f"*{physio_data['notes']}*",
            inline=False
        )

    icon_url = client_user.display_avatar.url if client_user else pic.BOT_AVATAR
    embed.set_footer(text=FOOTER_TEXT, icon_url=icon_url)
    return embed

