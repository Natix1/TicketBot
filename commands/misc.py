import discord
import config
import helpers.persistent_store as persistent_store

from views.create_ticket import CreateTicketView
from discord.ext import commands
from discord import app_commands
from time import time

class Misc(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @app_commands.command(name="ping", description="Check bot latency")
    @app_commands.guilds(discord.Object(config.GUILD_ID))

    async def ping(self, interaction: discord.Interaction):
        elapsed_recvMs = round((time() - interaction.created_at.timestamp()) * 1000)
        gatewayPingMs = round(self.bot.latency * 1000)

        await interaction.response.send_message(embed=discord.Embed(
            title="Pong",
            description=f"""
            **Message received in: ** {elapsed_recvMs}ms
            **Gateway ping**: {gatewayPingMs}ms
            """,
            color=config.SUCCESS_COLOR
        ))

    @app_commands.command(name="send-panel", description="Sends the panel to create tickets")
    @app_commands.describe(channel="Channel to which the panel is sent")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.guilds(discord.Object(config.GUILD_ID))
    
    async def send_panel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.defer()

        await channel.send(
            embed=discord.Embed(
                title="Tickets",
                description="Need help? Open a ticket down below!",
                color=config.INFO_COLOR
            ),
            view=CreateTicketView()
        )

        await interaction.followup.send("Created panel!")

    @app_commands.command(name="set-greeting", description="Sets the greeting sent when you claim the ticket.")
    @app_commands.describe(greeting="The greeting to be sent.")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.guilds(discord.Object(config.GUILD_ID))
    async def set_greeting(self, interaction: discord.Interaction, greeting: str | None):
        await interaction.response.defer()

        if not isinstance(interaction.user, discord.Member):
            return

        if greeting == "":
            greeting = None

        old_greeting = persistent_store.get_greeting(interaction.user)

        try:
            persistent_store.update_greeting(interaction.user, greeting)
        except Exception as e:
            await interaction.followup.send(f"Failed updating your greeting")
            return
        
        await interaction.followup.send(
            embed=discord.Embed(
                title="Greeting updated",
                description=f"Old greeting: {old_greeting or "None"}\nNew greeting: {greeting}",
                color=config.SUCCESS_COLOR
            )
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Misc(bot))