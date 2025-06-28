import discord
import helpers.persistent_store as persistent_store
import config

from discord.ext import commands
from discord import app_commands

class ManagementCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="transcripts", description="Gets an user's transcripts")
    @app_commands.describe(user="User to fetch transcripts from")
    @app_commands.checks.has_permissions(manage_guild = True)
    @app_commands.guilds(discord.Object(config.GUILD_ID))
    async def transcripts(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.response.defer()

        transcripts = persistent_store.get_user_transcripts(user)

        if not transcripts:
            await interaction.followup.send(
                embed=discord.Embed(
                    title=f"{user.name}'s Transcripts",
                    description="No transcripts found.",
                    color=config.INFO_COLOR
                ),
                ephemeral=True
            )
            return

        content_lines = []

        for ind, trans in enumerate(transcripts, start=1):
            timestamp = round(trans.created_at.timestamp())
            content_lines.append(
                f"**{ind}. Reason:** {trans.reason or '*No reason provided*'}\n"
                f"**Created at:** <t:{timestamp}>\n"
                f"**Link:** [View Transcript]({trans.url})"
            )

        embed = discord.Embed(
            title=f"{user.name}'s Transcripts",
            description="\n\n".join(content_lines),
            color=config.INFO_COLOR
        )

        if user.avatar:
            embed.set_thumbnail(url=user.avatar.url)

        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ManagementCommands(bot))