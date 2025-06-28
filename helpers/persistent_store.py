import os
import sqlite3
import config
import discord
import helpers.sourcebin as sourcebin

from dataclasses import dataclass
from typing import Optional, Literal
from datetime import datetime
from datetime import timezone
from bot import bot
from time import time
from discord.utils import escape_mentions

@dataclass
class Transcript:
    url: str
    reason: str
    created_at: datetime

def initialize_db():
    os.makedirs("data", exist_ok=True)
    with get_connection() as conn:
        cursor = conn.cursor()
        with open(config.SCHEMA_PATH, "r") as f:
            cursor.executescript(f.read())
        conn.commit()

def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(config.DB_PATH)

def get_greeting(member: discord.Member):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT greeting FROM greetings WHERE user_id = ?", (member.id,))
        row = cursor.fetchone()
        return row[0] if row else None

def update_greeting(member: discord.Member, greeting: str | None):
    with get_connection() as conn:
        cursor = conn.cursor()
        if greeting is None:
            cursor.execute("DELETE FROM greetings WHERE user_id = ?", (member.id,))
        else:
            update_greeting(member, None) # not ideal. but who cares, its just sqlite anyway
            cursor.execute("INSERT INTO greetings (user_id, greeting) VALUES (?, ?) ", (member.id, escape_mentions(greeting)))
        conn.commit()

def add_transcript(member: discord.Member, transcript_url: str, reason: str):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("INSERT INTO transcripts (creator_id, url, reason) VALUES (?, ?, ?)", (member.id, transcript_url, reason))
        conn.commit()

def get_user_transcripts(member: discord.Member) -> list[Transcript]:
    transcripts: list[Transcript] = []
        
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT url, reason, created_at FROM transcripts WHERE creator_id = ?", (member.id,))
        transcripts_resp = cursor.fetchall()

        for transcript in transcripts_resp:
            url, reason, created_at = transcript
            transcripts.append(Transcript(
                url,
                reason,
                datetime.fromisoformat(created_at)
            ))

    return sorted(transcripts, key=lambda t: t.created_at, reverse=True)

@dataclass
class Ticket:
    ticket_id: int
    channel: discord.TextChannel
    creator: discord.Member
    claimed_by: Optional[discord.Member]
    status: Literal["open", "claimed", "closed"]
    reason: str

    def Update(self):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE tickets SET
                    channel_id = ?,
                    creator_id = ?,
                    claimed_by = ?,
                    status = ?,
                    reason = ?
                WHERE ticket_id = ?
            """, (
                self.channel.id,
                self.creator.id,
                self.claimed_by.id if self.claimed_by else None,
                self.status,
                self.reason,
                self.ticket_id
            ))
            conn.commit()

    def SQL_Delete(self):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tickets WHERE ticket_id = ?", (self.ticket_id,))
            conn.commit()

    def SQL_Create(self):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tickets (
                    channel_id,
                    creator_id,
                    claimed_by,
                    status,
                    reason
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                self.channel.id,
                self.creator.id,
                self.claimed_by.id if self.claimed_by else None,
                self.status,
                self.reason
            ))
            conn.commit()
            self.ticket_id = cursor.lastrowid or -1

    def Save(self):
        return self.Update()

    async def Claim(self, member: discord.Member):
        if not member.guild_permissions.manage_guild:
            raise Exception("User does not have permission to claim the ticket")

        self.claimed_by = member
        self.status = "claimed"

        await self.channel.send(embed=discord.Embed(
            title="Claimed",
            description=f"Claimed by {member.name}",
            color=config.INFO_COLOR
        ))

        greeting = get_greeting(member)
        if greeting and member.avatar:
            webhook = await self.channel.create_webhook(name=member.name)
            await webhook.send(
                content=greeting,
                username=member.name,
                avatar_url=member.avatar.url,
            )
            await webhook.delete()

        self.Save()

    async def Close(self, member: discord.Member):
        if not member.guild_permissions.manage_guild:
            raise Exception("User does not have permission to close the ticket")

        if self.claimed_by != member:
            raise Exception("User trying to close the ticket isn't the claimee")

        self.closed_at = datetime.now()
        self.status = "closed"

        await self.channel.send(embed=discord.Embed(
            title="Closed",
            description=f"Closed by <@{member.id}>",
            color=config.ERROR_COLOR
        ))

        self.Save()

    async def Delete(self, member: discord.Member):
        if self.status != "closed":
            raise Exception("Tried deleting a ticket that isn't closed")

        if not member.guild_permissions.manage_guild:
            raise Exception("User does not have permission to delete the ticket")

        if self.claimed_by != member:
            raise Exception("User trying to delete the ticket isn't the claimee")

        await self.channel.delete(reason=f"Ticket closed by {member.id}")

        self.SQL_Delete()

    async def Unclaim(self, member: discord.Member):
        if not self.claimed_by:
            raise Exception(f"This ticket isn't claimed!")
        
        if self.claimed_by != member:
            raise Exception(f"You didn't claim this ticket! It's claimed by <@{self.claimed_by.id}>!")

        self.claimed_by = None
        self.status = "open"

        await self.channel.send(embed=discord.Embed(
            title="Unclaimed",
            description=f"Unclaimed, previous claimee: <@{member.id}>"
        ))

        self.Save()

    async def Transfer(self, member: discord.Member, new_claimee: discord.Member):
        if not self.claimed_by:
            raise Exception(f"This ticket isn't claimed!")
        
        if self.claimed_by != member:
            raise Exception(f"You didn't claim this ticket! It's claimed by <@{self.claimed_by.id}>!")

        guild = bot.get_guild(config.GUILD_ID)
        assert guild, "Guild not found"

        if not new_claimee.guild_permissions.manage_guild:
            raise Exception("The person you're trying to transfer to doesn't have permission to claim tickets!")

        self.claimed_by = new_claimee
        self.status = "claimed"

        await self.channel.send(embed=discord.Embed(
            title="Claimee transferred",
            description=f"Old claimee: <@{member.id}>\nNew claimee: <@{new_claimee.id}>"
        ))

        self.Save()

    async def GenerateTranscript(self, member: discord.Member):
        if not member.guild_permissions.manage_guild:
            raise Exception("User doesn't have permission to generate transcripts")
        
        if self.status != "closed":
            raise Exception("You can only generate transcripts on closed tickets!")
        
        start_time = time()
        await self.channel.send(
            embed=discord.Embed(
                title="Generating transcript...",
                description="This shouldn't take too long, but it is dependent on how much messages were being sent.",
                color=config.INFO_COLOR
            )
        )

        messages: list[discord.Message] = []
        async for message in self.channel.history(limit=None):
            messages.append(message)

        messages.reverse()

        content = f"""
Ticket tool by @natix1

Created by: @{self.creator.name} (ID: {self.creator.id})
Transcript reason: {self.reason}
Ticket opened at: {self.channel.created_at.strftime("%d/%m/%Y %H:%M:%S") + " UTC"}
Transcript saved at: {datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S") + " UTC"}
Message count: {len(messages)}

"""
        for message in messages:
            if message.content == "":
                continue

            content += f"@{message.author.name}: {message.content}\n"

        url = await sourcebin.paste(content)

        end_time = time()
        elapsedMs = round((end_time - start_time) * 1000)

        add_transcript(self.creator, url, self.reason)

        await self.channel.send(
            embed=discord.Embed(
                title="Transcript generated",
                description=f"Transcript generated in {elapsedMs}ms\nYou can view it [here]({url})",
                color=config.SUCCESS_COLOR
            ),
        )
        

async def clean_invalid_entries():
    with get_connection() as conn:
        cursor = conn.cursor()
        guild = await bot.fetch_guild(config.GUILD_ID)

        cursor.execute("SELECT channel_id FROM tickets")
        channel_ids = cursor.fetchall()

        for channel_id in channel_ids:
            channel_id = channel_id[0]
            channel = guild.get_channel(channel_id)
            if channel:
                continue
            try:
                channel = await guild.fetch_channel(channel_id)
            except discord.NotFound:
                cursor.execute("DELETE FROM tickets WHERE channel_id = ?", (channel_id,))

        conn.commit()

async def get_ticket_by_channel_id(channel_id: int) -> Ticket | None:
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        guild = bot.get_guild(config.GUILD_ID) or await bot.fetch_guild(config.GUILD_ID)

        cursor.execute("SELECT * FROM tickets WHERE channel_id = ?", (channel_id,))
        row = cursor.fetchone()
        if not row:
            return None

        try:
            channel_untyped = guild.get_channel(channel_id) or await guild.fetch_channel(channel_id)
            if not isinstance(channel_untyped, discord.TextChannel):
                return None
            channel = channel_untyped

            creator = guild.get_member(row["creator_id"]) or await guild.fetch_member(row["creator_id"])
            claimed_by = None
            if row["claimed_by"]:
                claimed_by = guild.get_member(row["claimed_by"]) or await guild.fetch_member(row["claimed_by"])

        except Exception as e:
            print(e)
            return None

        return Ticket(
            ticket_id=row["ticket_id"],
            channel=channel,
            creator=creator,
            claimed_by=claimed_by,
            status=row["status"],
            reason=row["reason"]
        )

async def get_ticket_by_ticket_id(ticket_id: int) -> Ticket | None:
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        guild = bot.get_guild(config.GUILD_ID) or await bot.fetch_guild(config.GUILD_ID)

        cursor.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,))
        row = cursor.fetchone()
        if not row:
            return None

        try:
            channel_untyped = guild.get_channel(row["channel_id"]) or await guild.fetch_channel(row["channel_id"])
            if not isinstance(channel_untyped, discord.TextChannel):
                return None
            channel = channel_untyped

            creator = guild.get_member(row["creator_id"]) or await guild.fetch_member(row["creator_id"])
            claimed_by = None
            if row["claimed_by"]:
                claimed_by = guild.get_member(row["claimed_by"]) or await guild.fetch_member(row["claimed_by"])

        except Exception as e:
            print(e)
            return None

        return Ticket(
            ticket_id=row["ticket_id"],
            channel=channel,
            creator=creator,
            claimed_by=claimed_by,
            status=row["status"],
            reason=row["reason"]
        )
