import sys

from config import BOT_TOKEN, logger
from core.bot import ElvieBot


def main() -> None:
    """Main entrypoint to run the Elvie Discord bot."""
    if not BOT_TOKEN:
        logger.error("Błąd: Brak zmiennej BOT_TOKEN w pliku .env!")
        sys.exit(1)

    bot = ElvieBot()
    bot.run(BOT_TOKEN)


if __name__ == "__main__":
    main()