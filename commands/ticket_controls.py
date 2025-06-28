import discord
import config
import helpers.persistent_store as persistent_store

from discord.ext import commands
from discord import app_commands

class TicketControls(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="claim", description="Claims the ticket")
    @app_commands.checks.has_permissions(manage_guild = True)
    @app_commands.guilds(discord.Object(config.GUILD_ID))
    async def claim(self, interaction: discord.Interaction):
        if not isinstance(interaction.user, discord.Member):
            return
        
        await interaction.response.defer()
        
        if not interaction.channel:
            await interaction.followup.send("Failed looking up ticket. Maybe you're running this in the wrong channel?", ephemeral=True)
            return

        ticket = await persistent_store.get_ticket_by_channel_id(interaction.channel.id)
        if not ticket:
            await interaction.followup.send("It seems you're in a channel that isn't a ticket.", ephemeral=True)
            return

        try:
            await ticket.Claim(interaction.user)
        except Exception as e:
            await interaction.followup.send(content=str(e), ephemeral=True)
            return
        
        await interaction.followup.send("Ticket claimed succesfully!", ephemeral=True)

    @app_commands.command(name="unclaim", description="Unclaims the ticket")
    @app_commands.checks.has_permissions(manage_guild = True)
    @app_commands.guilds(discord.Object(config.GUILD_ID))
    async def unclaim(self, interaction: discord.Interaction):
        if not isinstance(interaction.user, discord.Member):
            return
        
        await interaction.response.defer()

        if not interaction.channel:
            await interaction.followup.send("Failed looking up ticket. Maybe you're running this in the wrong channel?", ephemeral=True)
            return
        
        ticket = await persistent_store.get_ticket_by_channel_id(interaction.channel.id)
        if not ticket:
            await interaction.followup.send("It seems you're in a channel that isn't a ticket.", ephemeral=True)
            return
        
        try:
            await ticket.Unclaim(interaction.user)
        except Exception as e:
            await interaction.followup.send(content=str(e), ephemeral=True)
            return
        
        await interaction.followup.send("Ticket unclaimed succesfully!", ephemeral=True)

    @app_commands.command(name="transfer", description="Transfers the ticket")
    @app_commands.describe(to="Who to transfer the ticket to?")
    @app_commands.checks.has_permissions(manage_guild = True)
    @app_commands.guilds(discord.Object(config.GUILD_ID))
    async def transfer(self, interaction: discord.Interaction, to: discord.Member):
        if not isinstance(interaction.user, discord.Member):
            return
        
        await interaction.response.defer()

        if not interaction.channel:
            await interaction.followup.send("Failed looking up ticket. Maybe you're running this in the wrong channel?", ephemeral=True)
            return
        
        ticket = await persistent_store.get_ticket_by_channel_id(interaction.channel.id)
        if not ticket:
            await interaction.followup.send("It seems you're in a channel that isn't a ticket.", ephemeral=True)
            return
        
        try:
            await ticket.Transfer(interaction.user, to)
        except Exception as e:
            await interaction.followup.send(content=str(e), ephemeral=True)
            return
        
        await interaction.followup.send("Ticket transferred succesfully!", ephemeral=True)

    @app_commands.command(name="close", description="Closes the ticket")
    @app_commands.checks.has_permissions(manage_guild = True)
    @app_commands.guilds(discord.Object(config.GUILD_ID))
    async def close(self, interaction: discord.Interaction):
        if not isinstance(interaction.user, discord.Member):
            return
        
        await interaction.response.defer()

        if not interaction.channel:
            await interaction.followup.send("Failed looking up ticket. Maybe you're running this in the wrong channel?", ephemeral=True)
            return
        
        ticket = await persistent_store.get_ticket_by_channel_id(interaction.channel.id)
        if not ticket:
            await interaction.followup.send("It seems you're in a channel that isn't a ticket.", ephemeral=True)
            return
        
        try:
            await ticket.Close(interaction.user)
        except Exception as e:
            await interaction.followup.send(content=str(e))
            return
        
        await interaction.followup.send("Ticket closed succesfully!", ephemeral=True)

    @app_commands.command(name="delete", description="Deletes the ticket")
    @app_commands.checks.has_permissions(manage_guild = True)
    @app_commands.guilds(discord.Object(config.GUILD_ID))
    async def delete(self, interaction: discord.Interaction):
        if not isinstance(interaction.user, discord.Member):
            return
        
        await interaction.response.defer()

        if not interaction.channel:
            await interaction.followup.send("Failed looking up ticket. Maybe you're running this in the wrong channel?", ephemeral=True)
            return
        
        ticket = await persistent_store.get_ticket_by_channel_id(interaction.channel.id)
        if not ticket:
            await interaction.followup.send("It seems you're in a channel that isn't a ticket.", ephemeral=True)
            return
        
        await interaction.followup.send("Deleting ticket...")

        try:
            await ticket.Delete(interaction.user)
        except Exception as e:
            await interaction.followup.send(content=str(e), ephemeral=True)
            return

    @app_commands.command(name="transcript", description="Generates a transcript")
    @app_commands.checks.has_permissions(manage_guild = True)
    @app_commands.guilds(discord.Object(config.GUILD_ID))
    async def transcript(self, interaction: discord.Interaction):
        if not isinstance(interaction.user, discord.Member):
            return
        
        await interaction.response.defer()

        if not interaction.channel:
            await interaction.followup.send("Failed looking up ticket. Maybe you're running this in the wrong channel?", ephemeral=True)
            return
        
        ticket = await persistent_store.get_ticket_by_channel_id(interaction.channel.id)
        if not ticket:
            await interaction.followup.send("It seems you're in a channel that isn't a ticket.", ephemeral=True)
            return
        
        try:
            await ticket.GenerateTranscript(interaction.user)
        except Exception as e:
            await interaction.followup.send(content=str(e), ephemeral=True)

        await interaction.followup.send(content="Generated transcript succesfully!", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(TicketControls(bot))