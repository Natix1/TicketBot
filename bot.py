import discord
import config

from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(config.COMMAND_PREFIX, intents=intents)