import discord
from discord import app_commands
import os
import datetime

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# ---------------- READY EVENT ---------------- #
@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("Bot is online and slash commands are synced.")

# ---------------- MODERATION COMMANDS ---------------- #

@tree.command(name="kick", description="Kick a member from the server")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"✔ {member} has been kicked. Reason: {reason}")

@tree.command(name="ban", description="Ban a member from the server")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"✔ {member} has been banned. Reason: {reason}")

@tree.command(name="unban", description="Unban a user by ID")
@app_commands.checks.has_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, user_id: str):
    try:
        user = await client.fetch_user(int(user_id))
        await interaction.guild.unban(user)
        await interaction.response.send_message(f"✔ {user} has been unbanned.")
    except:
        await interaction.response.send_message("❌ Invalid user ID.", ephemeral=True)

@tree.command(name="clear", description="Delete a number of messages")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    if amount <= 0:
        await interaction.response.send_message("⚠ Please provide a number greater than 0.", ephemeral=True)
        return

    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"✔ Deleted {amount} messages.", ephemeral=True)

@tree.command(name="mute", description="Timeout a member (in minutes)")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int):
    try:
        until = discord.utils.utcnow() + datetime.timedelta(minutes=minutes)
        await member.timeout(until)
        await interaction.response.send_message(f"✔ {member} has been muted for {minutes} minutes.")
    except:
        await interaction.response.send_message("❌ Failed to mute the member.", ephemeral=True)

@tree.command(name="unmute", description="Remove timeout from a member")
@app_commands.checks.has_permissions(moderate_members=True)
async def unmute(interaction: discord.Interaction, member: discord.Member):
    try:
        await member.timeout(None)
        await interaction.response.send_message(f"✔ {member} has been unmuted.")
    except:
        await interaction.response.send_message("❌ Failed to unmute the member.", ephemeral=True)

# ---------------- ERROR HANDLER ---------------- #
@kick.error
@ban.error
@unban.error
@clear.error
@mute.error
@unmute.error
async def permission_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)

# ---------------- RUN ---------------- #
client.run(TOKEN)
