import unicodedata
from typing import Optional

import discord

from config import FOOTER_TEXT, MAIN_COLOR
import content.pictures as pic

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
