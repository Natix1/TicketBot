import discord

from discord import app_commands

async def on_tree_error(interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
    if isinstance(error, app_commands.MissingPermissions):
        try:
            await interaction.response.send_message("You're missing permissions to do that!")
        except discord.NotFound:
            pass

    elif isinstance(error, app_commands.CommandOnCooldown):
        try:
            await interaction.response.send_message("Slow down! You're running this command too often!")
        except discord.NotFound:
            pass
    else:
        print(error.add_note(f"Error while handling interaction for user {interaction.user.name}"), flush=True)
        raise error