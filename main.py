import discord
from discord.ext import commands  # Prefix commands ke liye zaroori
from discord import app_commands
import os
import datetime

TOKEN = os.getenv("TOKEN")

# Intents setup (Prefix commands ke liye Message Content intent zaroori hai)
intents = discord.Intents.all()

# 'Client' ki jagah 'Bot' use kar rahe hain taaki dono kaam karein
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------- READY EVENT ---------------- #
@bot.event
async def on_ready():
    # bot.tree slash commands ko sync karega
    await bot.tree.sync()
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Bot is online. Both Slash (/) and Prefix (!) commands are ready.")

# ---------------- PREFIX COMMAND EXAMPLES ---------------- #

@bot.command()
async def hello(ctx):
    """Simple Prefix Command: !hello"""
    await ctx.send(f"Hello {ctx.author.mention}! Prefix command sahi se kaam kar raha hai.")

@bot.command()
@commands.has_permissions(kick_members=True)
async def pkick(ctx, member: discord.Member, *, reason="No reason provided"):
    """Prefix Kick: !pkick @user Reason"""
    await member.kick(reason=reason)
    await ctx.send(f"✔ {member} has been kicked via prefix command.")

# ---------------- SLASH COMMANDS (MODERATION) ---------------- #

@bot.tree.command(name="kick", description="Kick a member from the server")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"✔ {member} has been kicked. Reason: {reason}")

@bot.tree.command(name="ban", description="Ban a member from the server")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"✔ {member} has been banned. Reason: {reason}")

@bot.tree.command(name="unban", description="Unban a user by ID")
@app_commands.checks.has_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, user_id: str):
    try:
        user = await bot.fetch_user(int(user_id))
        await interaction.guild.unban(user)
        await interaction.response.send_message(f"✔ {user} has been unbanned.")
    except:
        await interaction.response.send_message("❌ Invalid user ID.", ephemeral=True)

@bot.tree.command(name="clear", description="Delete a number of messages")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    if amount <= 0:
        await interaction.response.send_message("⚠ Please provide a number greater than 0.", ephemeral=True)
        return
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"✔ Deleted {amount} messages.", ephemeral=True)

@bot.tree.command(name="mute", description="Timeout a member (in minutes)")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int):
    try:
        until = discord.utils.utcnow() + datetime.timedelta(minutes=minutes)
        await member.timeout(until)
        await interaction.response.send_message(f"✔ {member} has been muted for {minutes} minutes.")
    except:
        await interaction.response.send_message("❌ Failed to mute the member.", ephemeral=True)

@bot.tree.command(name="unmute", description="Remove timeout from a member")
@app_commands.checks.has_permissions(moderate_members=True)
async def unmute(interaction: discord.Interaction, member: discord.Member):
    try:
        await member.timeout(None)
        await interaction.response.send_message(f"✔ {member} has been unmuted.")
    except:
        await interaction.response.send_message("❌ Failed to unmute the member.", ephemeral=True)

# ---------------- ERROR HANDLERS ---------------- #

# Slash Error Handler
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ You don't have permission for this slash command.", ephemeral=True)

# Prefix Error Handler
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this prefix command.")

# ---------------- RUN ---------------- #
bot.run(TOKEN)
