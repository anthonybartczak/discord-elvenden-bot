import re
from typing import Dict, List, Optional, Tuple

import discord

from config import FOOTER_TEXT, MAIN_COLOR
import content.pictures as pic

# Map of characteristic codes to full Polish names and representative emojis
ATTRIBUTE_MAP: Dict[str, str] = {
    "WW": "🎯 WW (Walka Wręcz)",
    "US": "🏹 US (Umiejętności Strzeleckie)",
    "S": "💪 S (Siła)",
    "Wt": "🛡️ Wt (Wytrzymałość)",
    "I": "⚡ I (Inicjatywa)",
    "Zw": "🏃 Zw (Zwinność)",
    "Zr": "🖐️ Zr (Zręczność)",
    "Int": "🧠 Int (Inteligencja)",
    "SW": "🔮 SW (Siła Woli)",
    "Ogd": "👑 Ogd (Ogłada)",
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
        r"\n\n🎯 **Przykładowe Specjalizacje:**\n",
        cleaned,
        flags=re.IGNORECASE
    )
    cleaned = re.sub(
        r"(?<=[.!?])\s*(Specjalizacje:\s*)",
        r"\n\n🎯 **Specjalizacje:**\n",
        cleaned,
        flags=re.IGNORECASE
    )
    cleaned = re.sub(
        r"(?<=[.!?])\s*(W walce\b)",
        r"\n\n⚔️ **W walce:** W walce",
        cleaned,
        flags=re.IGNORECASE
    )
    cleaned = re.sub(
        r"(?<=[.!?])\s*(Więcej informacji na ten temat znajduje się\b)",
        r"\n\n📖 Więcej informacji na ten temat znajduje się",
        cleaned,
        flags=re.IGNORECASE
    )
    cleaned = re.sub(
        r"(?<=[.!?])\s*(Uwaga:\s*)",
        r"\n\n⚠️ **Uwaga:** ",
        cleaned,
        flags=re.IGNORECASE
    )

    # If text is still a single monolithic block without paragraphs (and longer than 400 chars),
    # break naturally after sentences that end with a period.
    if "\n\n" not in cleaned and len(cleaned) > 400:
        sentences = re.split(r"(?<=[.!?])\s+", cleaned)
        paragraphs = []
        current_p = []
        curr_len = 0
        for s in sentences:
            current_p.append(s)
            curr_len += len(s)
            if curr_len >= 280:
                paragraphs.append(" ".join(current_p))
                current_p = []
                curr_len = 0
        if current_p:
            paragraphs.append(" ".join(current_p))
        cleaned = "\n\n".join(paragraphs)

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
    """Formats a list of talents into Discord backtick chips."""
    if not talents:
        return "Brak powiązanych talentów"
    return " • ".join(f"`{t}`" for t in talents)


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
    type_emoji = "🟢" if "podstawowa" in ab_type.lower() else "🔵"
    embed.add_field(name="🏷️ Typ", value=f"{type_emoji} **{ab_type}**", inline=True)
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
    embed.add_field(name="🏛️ Dostępne dla kultów", value=cults_str or "Brak", inline=False)
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
                f"🎯 **Zasięg:** `{b_range}` • 👥 **Cel:** `{b_targets}` • ⏳ **Czas:** `{b_dur}`\n"
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
