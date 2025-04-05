import discord
from bs4 import BeautifulSoup
import envactions

channel_messages = {}

def add_message(message: discord.Message):
    if message.channel.id not in channel_messages:
        channel_messages[message.channel.id] = []
    
    channel_messages[message.channel.id].append(message)

def generate_transcript(channelID: int, title: str):
    if channelID not in channel_messages or not channel_messages[channelID]:
        return None

    transcript_html = envactions.get_transcript_html()
    soup = BeautifulSoup(transcript_html, "html.parser")

    messages_section = soup.find(id="messages")

    for message in channel_messages[channelID]:
        message_div = soup.new_tag('div', **{'class': 'message'})
        
        username_span = soup.new_tag('span', **{'class': 'username'})
        username_span.string = message.author.name

        timestamp_span = soup.new_tag('span', **{'class': 'time'})
        timestamp_span.string = message.created_at.strftime('%Y-%m-%d %H:%M:%S')
        
        content_div = soup.new_tag('div', **{'class': 'content'})
        content_div.string = message.content

        message_div.append(username_span)
        message_div.append(' ')
        message_div.append(timestamp_span)
        message_div.append(content_div)

        title_h1 = soup.find(id="title")
        title_h1.string = title

        messages_section.append(message_div)

    return str(soup.prettify())