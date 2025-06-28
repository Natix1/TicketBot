import discord
import config
import helpers.persistent_store as persistent_store

from discord.ext import commands, tasks

class CleanInvalidEntries(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @tasks.loop(seconds=config.INVALID_CHECK_INTERVAL)
    async def clear_invalid_entries(self):
        await persistent_store.clean_invalid_entries()

    async def cog_load(self):
        self.clear_invalid_entries.start()

    async def cog_unload(self):
        self.clear_invalid_entries.cancel()

async def setup(bot: commands.Bot):
    await bot.add_cog(CleanInvalidEntries(bot))