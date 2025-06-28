import discord
import config

from discord.ext import commands
from views.create_ticket import CreateTicketView

class RegisterUIViews(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(CreateTicketView())

        print("Added UIViews")

async def setup(bot: commands.Bot):
    await bot.add_cog(RegisterUIViews(bot))