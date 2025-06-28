import discord
import config

from discord.ext import commands

class InitMessage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.user:
            raise Exception("Failed logging in to discord!")
        
        print(f"Logged in as {self.bot.user} (ID: {self.bot.user.id})!")

async def setup(bot: commands.Bot):
    await bot.add_cog(InitMessage(bot))