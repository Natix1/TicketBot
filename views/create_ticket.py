import discord
import helpers.persistent_store as persistent_store
import config

from discord import ui
from bot import bot
from datetime import datetime

class ReasonModal(ui.Modal, title="Create a ticket"):
    reason = ui.TextInput(label="Reason for the ticket", placeholder="I want to open this ticket because...", required=True, min_length=4, max_length=255)
    
    async def on_submit(self, interaction: discord.Interaction):
        if not isinstance(interaction.user, discord.Member):
            return
        
        await interaction.response.defer()

        guild = bot.get_guild(config.GUILD_ID)
        category = bot.get_channel(config.TICKETS_CATEGORY) or await bot.fetch_channel(config.TICKETS_CATEGORY)

        if category and not isinstance(category, discord.CategoryChannel):
            raise Exception("Category ID invalid")

        assert guild, "Guild not found"

        new_channel = await guild.create_text_channel(name=f"ticket-{interaction.user.name}", reason=f"Ticket opened by user {interaction.user.id}", category=category)
        assert new_channel, "Failed creating channel"

        ticket: persistent_store.Ticket = persistent_store.Ticket(
            ticket_id=-1,
            channel=new_channel,
            creator=interaction.user,
            claimed_by=None,
            status='open',
            reason=self.reason.value,
        )

        ticket.SQL_Create()

        await interaction.followup.send(f"Ticket created! {new_channel.jump_url}", ephemeral=True)
        await new_channel.send(
            content=f"<@{interaction.user.id}>",
            embed=discord.Embed(
                title=f"New ticket by {interaction.user.name}",
                description=f"Reason: {ticket.reason}",
                color=config.SUCCESS_COLOR
            )
)

class CreateTicketView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="➕ Create a ticket", style=discord.ButtonStyle.gray, custom_id="persistent:create_ticket")
    async def click(self, interaction: discord.Interaction, button: ui.Button):
        if not isinstance(interaction.user, discord.Member):
            return
        
        await interaction.response.send_modal(ReasonModal())