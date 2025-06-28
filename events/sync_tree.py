import config
import discord

from time import time
from discord.ext import commands

class OnReady(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Syncing command tree and fetching main guild...")
        
        start_time = time()

        guild = await self.bot.fetch_guild(config.GUILD_ID)
        if not guild:
            print("Failed fetching guild set in config.py!")
            return
        
        await self.bot.tree.sync(guild=discord.Object(config.GUILD_ID))
        end_time = time()

        elapsedMs = round((end_time - start_time) * 1000)

        print(f"Synced command tree to guild {guild.name} in {elapsedMs}ms")


async def setup(bot: commands.Bot):
    await bot.add_cog(OnReady(bot))