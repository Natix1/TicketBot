import os

from discord.ext.commands import when_mentioned_or
from dotenv import load_dotenv

load_dotenv()

TICKETS_CATEGORY = 1388184471051698267

TOKEN = os.getenv("TOKEN") or ""
if TOKEN == "":
    raise Exception("Token not set in environment variables. Create a .env file and put your token in the format 'TOKEN=(Your token)'")

DEVS = [955090007335530506]
DB_PATH = "data/data.db"
SCHEMA_PATH = "data/schema.sql"

INVALID_CHECK_INTERVAL = 5

GUILD_ID = 1276551786987262115
SUCCESS_COLOR = 0x21de11
INFO_COLOR = 0x11a6de
WARN_COLOR = 0xdecb11
ERROR_COLOR = 0xde3811

COMMAND_PREFIX = when_mentioned_or()