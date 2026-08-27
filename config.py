import logging
import os
from pathlib import Path
from dotenv import load_dotenv

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
