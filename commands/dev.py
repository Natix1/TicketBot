import discord
import config

from discord.ext import commands
from discord import app_commands
from helpers.extensions import extensions
from time import time

class Dev(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="reload-cog", description="Reloads a cog.")
    @app_commands.describe(cog_name="Cog name ('*' chooses all)")
    @app_commands.guilds(discord.Object(config.GUILD_ID))
    @app_commands.checks.has_permissions(administrator=True)
    async def reload_cog(self, interaction: discord.Interaction, cog_name: str):
        await interaction.response.defer()

        start_time = time()

        try:
            
            if cog_name == "*":
                for ext in extensions:
                    await self.bot.reload_extension(ext)
            else:
                await self.bot.reload_extension(cog_name)

        except Exception as e:
            await interaction.followup.send(embed=discord.Embed(
                title="Error",
                description=f"❌ Error when reloading cog(s) {cog_name}: {e}",
                color=config.ERROR_COLOR
            ))
            return

        end_time = time()
        elapsedMs = round((end_time - start_time) * 1000)

        await interaction.followup.send(embed=discord.Embed(
            title="✅ Success",
            description=f"Reload cog(s) {cog_name} in {elapsedMs}ms.",
            color=config.SUCCESS_COLOR
        ))

    @app_commands.command(name="resync-tree", description="Re-syncs the command tree.")
    @app_commands.guilds(discord.Object(config.GUILD_ID))
    @app_commands.checks.has_permissions(administrator=True)
    async def resync_tree(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.followup.send("Syncing command tree...", ephemeral=True)
        start_time = time()
        try:
            await self.bot.tree.sync(guild=discord.Object(config.GUILD_ID))
        except Exception as e:
            await interaction.followup.send("Failed resyncing the tree", ephemeral=True )
            print(e.add_note(f"Failed resyncing tree"))
            return

        end_time = time()
        elapsedMs = round((end_time - start_time) * 1000)

        await interaction.followup.send(f"Tree synced succesfully in {elapsedMs}ms", ephemeral=True )

async def setup(bot: commands.Bot):
    await bot.add_cog(Dev(bot))