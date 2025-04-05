import discord
import envactions
import time
import transcripts
import math

from discord import app_commands

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

TOKEN = envactions.GetBotToken()
ServerJSON = envactions.GetServerConfiguration()

GUILD_ID = ServerJSON.GuildID
PANEL_CHANNEL_ID = ServerJSON.ChannelID
CATEGORY_ID = ServerJSON.TicketsCategoryID

TICKET_CHANNEL_IDS = []

class RemovalPanel(discord.ui.View):
    @discord.ui.button(label = "Close", style = discord.ButtonStyle.primary, emoji = "❌")
    async def button_callback(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.send_message("Generating transcript...")

        transcript_html = transcripts.generate_transcript(interaction.channel.id, "#" + interaction.channel.name)

        userid = interaction.user.id
        unix_timestamp = math.floor(time.time())

        with open(f"./transcripts/user-{userid}-{unix_timestamp}.html", "w") as f:
            f.write(transcript_html)

        await interaction.followup.send("Transcript available " + f"[here](https://tickets.natixone.xyz/transcript/{userid}/{unix_timestamp})")
        await interaction.followup.send("Transcript generated and saved! Closing in 5 seconds...")

        time.sleep(5)
        await interaction.channel.delete()
        
        if interaction.channel.id in TICKET_CHANNEL_IDS:
            TICKET_CHANNEL_IDS.remove(interaction.channel.id)
        
class TicketPanel(discord.ui.View):
    @discord.ui.button(label = "Click here!", style = discord.ButtonStyle.primary, emoji="📥")
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

        embed = discord.Embed(
            title = "Support ticket",
            description=f"Opened by @{interaction.user.name}"
        )

        TICKET_CHANNEL_IDS.append(new_channel.id)

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
    print("Ready! " + "Logged in as " + client.user.name)

@client.event
async def on_message(message: discord.Message):
    if message.channel.id not in TICKET_CHANNEL_IDS:
        return
    
    transcripts.add_message(message=message)

client.run(TOKEN)