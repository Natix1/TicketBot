import discord
import envactions
import time
import transcripts
import math
import asyncio
import utils
import atexit

from discord import app_commands

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

TOKEN = envactions.GetBotToken()
ServerJSON = envactions.GetServerConfiguration()

GUILD_ID = ServerJSON.GuildID
PANEL_CHANNEL_ID = ServerJSON.ChannelID
CATEGORY_ID = ServerJSON.TicketsCategoryID
TRANSCRIPTS_CHANNEl_ID = ServerJSON.TranscriptsChannelID

TICKET_CHANNEL_IDS = utils.get_ticket_ids_from_disk()

def cleanup():
    print("Closing...")
    utils.dump_ticket_ids_to_disk(TICKET_CHANNEL_IDS)
    print("Done!")

class RemovalPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label = "Close", style = discord.ButtonStyle.primary, emoji = "❌", custom_id="ticket_close_button")
    async def button_callback(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.defer(ephemeral=True)

        transcript_html = transcripts.generate_transcript(interaction.channel.id, "#" + interaction.channel.name)

        userid = interaction.user.id
        unix_timestamp = math.floor(time.time())

        fileName = f"user-{userid}-{unix_timestamp}.html"
        with open("transcripts/" + fileName, "w") as f:
            f.write(transcript_html)

        embed = discord.Embed(
            title="Ticket transcript: " + interaction.channel.name,
            description=f"You can find the transcript [here.](https://tickets.natixone.xyz/transcripts/{userid}/{unix_timestamp})",
            color=0x00ff00
        )

        transcripts_channel = client.get_channel(TRANSCRIPTS_CHANNEl_ID)

        try:
            await interaction.user.send(content="", embed=embed)
        except discord.Forbidden:
            pass

        await interaction.channel.send(content="", embed=embed)
        await transcripts_channel.send(content="", embed=embed)

        await asyncio.sleep(4)
        await interaction.channel.delete()
        
        if interaction.channel.id in TICKET_CHANNEL_IDS:
            TICKET_CHANNEL_IDS.remove(interaction.channel.id)
            utils.dump_ticket_ids_to_disk(TICKET_CHANNEL_IDS)
        
class TicketPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label = "Click here!", style = discord.ButtonStyle.primary, emoji="📥", custom_id="ticket_create_button")
    async def button_callback(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.send_message("Creating ticket...", ephemeral=True)

        guild = client.get_guild(GUILD_ID)

        if not guild:
            raise discord.ClientException("Failed fetching guild")
        
        category = discord.utils.get(guild.categories, id = CATEGORY_ID)
        new_channel = await guild.create_text_channel(
            "Ticket-" + interaction.user.name,
            category=category
        )

        await new_channel.set_permissions(interaction.user, read_messages=True, send_messages=True)

        embed = discord.Embed(
            title = "Support ticket",
            description=f"Opened by @{interaction.user.name}"
        )

        TICKET_CHANNEL_IDS.append(new_channel.id)
        utils.dump_ticket_ids_to_disk(TICKET_CHANNEL_IDS)

        await new_channel.send(content=f"<@{interaction.user.id}>", embed=embed, view=RemovalPanel())
        await interaction.followup.send(f"Created ticket! <#{new_channel.id}>", ephemeral=True)

@tree.command(
    name = "sendcreatepanel",
    description = "Sends the ticket creation panel to the channel ID defined in data/server.json",
    guild=discord.Object(id=GUILD_ID)
)
async def handler(interaction: discord.Interaction):
    await interaction.response.send_message("Creating panel...", ephemeral=True)

    embed = discord.Embed(
        title = "Create a support ticket",
        description="Click the button below to talk to our support team!",
        color=0x00ff00
    )

    channel = client.get_channel(PANEL_CHANNEL_ID)
    if channel is not None:
        await channel.send(embed=embed, view=TicketPanel())
        await interaction.followup.send("Sent message to " + channel.name + "!", ephemeral=True)
    else:
        await interaction.followup.send("Failed to find the specified channel.", ephemeral=True)

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    client.add_view(TicketPanel())
    client.add_view(RemovalPanel())
    print(f"Ready! Logged in as {client.user.name}#{client.user.discriminator} with UserID {client.user.id}!")

@client.event
async def on_message(message: discord.Message):
    if message.channel.id not in TICKET_CHANNEL_IDS:
        return
    
    transcripts.add_message(message=message)

atexit.register(cleanup)
client.run(TOKEN)