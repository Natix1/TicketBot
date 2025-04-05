import json

from dotenv import load_dotenv
from os import environ
from dataclasses import dataclass

load_dotenv()

@dataclass
class ServerJSONConfig:
    GuildID: int
    ChannelID: int
    TicketsCategoryID: int

def GetBotToken() -> str:
    TOKEN = environ.get("TOKEN")
    if TOKEN == "":
        raise SystemExit("TOKEN not defined in .env!")
    
    return TOKEN

def get_transcript_html() -> str:
    with open("./templates/transcript.html", "r") as f:
        return f.read()

def GetServerConfiguration() -> ServerJSONConfig:
    contents = ""

    with open("./data/server.json", "r") as f:
        contents = json.load(f)

    config = ServerJSONConfig(
        GuildID=contents["GuildID"],
        ChannelID=contents["ChannelID"],
        TicketsCategoryID=contents["TicketsCategoryID"]
    )

    return config