import discord
from discord.ext import commands

from config import logger

EXTENSIONS = [
    "cogs.general",
    "cogs.mechanics",
    "cogs.compendium",
]


class ElvieBot(commands.Bot):
    """Custom Discord Bot with CommandTree synchronization and modular Cogs."""

    def __init__(self) -> None:
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self) -> None:
        for extension in EXTENSIONS:
            try:
                await self.load_extension(extension)
                logger.info("Załadowano moduł: %s", extension)
            except Exception as e:
                logger.error("Błąd podczas ładowania modułu %s: %s", extension, e, exc_info=True)

        logger.info("Synchronizowanie drzewa poleceń slash...")
        await self.tree.sync()
        logger.info("Drzewo poleceń zsynchronizowane pomyślnie.")

    async def on_ready(self) -> None:
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(name="/pomoc | WFRP 4e")
        )
        logger.info("Zalogowano jako %s (ID: %s)", self.user, self.user.id if self.user else "N/A")
