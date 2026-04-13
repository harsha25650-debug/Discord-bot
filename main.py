import discord
from discord import app_commands
import os
import datetime
import random

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# ---------------- PREFIX SYSTEM ---------------- #
prefixes = {}

def get_prefix(guild_id):
    return prefixes.get(guild_id, "!")

# ---------------- CASE LOG ---------------- #
async def log_case(guild, text):
    channel = discord.utils.get(guild.text_channels, name="mod-logs")
    if channel:
        await channel.send(text)

# ---------------- READY EVENT ---------------- #
@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user}")
    print("Bot is online and ready.")

# ---------------- HELP COMMAND ---------------- #
@tree.command(name="help", description="Show bot help menu")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📌 Bot Help Panel",
        description="""
Moderation:
/kick /ban /unban /mute /unmute /clear

Utility:
/say /dm /nick /inviteinfo

System:
/prefix /afk /giveaway
        """,
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)

# ---------------- SAY ---------------- #
@tree.command(name="say", description="Send a message as bot")
async def say(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)

# ---------------- DM ---------------- #
@tree.command(name="dm", description="Send DM to a user")
async def dm(interaction: discord.Interaction, member: discord.Member, message: str):
    await member.send(message)
    await interaction.response.send_message("✔ DM sent", ephemeral=True)

# ---------------- NICK ---------------- #
@tree.command(name="nick", description="Change nickname")
@app_commands.checks.has_permissions(manage_nicknames=True)
async def nick(interaction: discord.Interaction, member: discord.Member, name: str):
    await member.edit(nick=name)
    await interaction.response.send_message(f"✔ Nick changed for {member}")

# ---------------- INVITE INFO ---------------- #
@tree.command(name="inviteinfo", description="Show server invite count")
async def inviteinfo(interaction: discord.Interaction):
    invites = await interaction.guild.invites()
    await interaction.response.send_message(f"🔗 Total invites: {len(invites)}")

# ---------------- PREFIX CHANGE ---------------- #
@tree.command(name="prefix", description="Change server prefix (prefix system demo)")
async def prefix(interaction: discord.Interaction, new_prefix: str):
    prefixes[interaction.guild.id] = new_prefix
    await interaction.response.send_message(f"✔ Prefix changed to `{new_prefix}`")

# ---------------- AFK SYSTEM ---------------- #
afk_users = {}

@tree.command(name="afk", description="Set AFK status")
async def afk(interaction: discord.Interaction, reason: str = "AFK"):
    afk_users[interaction.user.id] = reason
    await interaction.response.send_message(f"😴 You are AFK: {reason}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.author.id in afk_users:
        afk_users.pop(message.author.id)
        await message.channel.send(f"👋 Welcome back {message.author}")

    for user in message.mentions:
        if user.id in afk_users:
            await message.channel.send(f"😴 {user} is AFK: {afk_users[user.id]}")

# ---------------- MODERATION ---------------- #
@tree.command(name="kick", description="Kick a member")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"✔ Kicked {member}")
    await log_case(interaction.guild, f"KICK | {member} | {reason}")

@tree.command(name="ban", description="Ban a member")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"✔ Banned {member}")
    await log_case(interaction.guild, f"BAN | {member} | {reason}")

@tree.command(name="unban", description="Unban user by ID")
@app_commands.checks.has_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, user_id: str):
    user = await client.fetch_user(int(user_id))
    await interaction.guild.unban(user)
    await interaction.response.send_message(f"✔ Unbanned {user}")
    await log_case(interaction.guild, f"UNBAN | {user}")

@tree.command(name="clear", description="Delete messages")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    if amount <= 0:
        await interaction.response.send_message("⚠ Invalid number", ephemeral=True)
        return

    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"✔ Deleted {amount} messages", ephemeral=True)

@tree.command(name="mute", description="Timeout a member")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int):
    until = discord.utils.utcnow() + datetime.timedelta(minutes=minutes)
    await member.timeout(until)
    await interaction.response.send_message(f"✔ Muted {member} for {minutes} minutes")
    await log_case(interaction.guild, f"MUTE | {member} | {minutes} min")

@tree.command(name="unmute", description="Remove timeout")
@app_commands.checks.has_permissions(moderate_members=True)
async def unmute(interaction: discord.Interaction, member: discord.Member):
    await member.timeout(None)
    await interaction.response.send_message(f"✔ Unmuted {member}")
    await log_case(interaction.guild, f"UNMUTE | {member}")

# ---------------- GIVEAWAY ---------------- #
@tree.command(name="giveaway", description="Start giveaway")
async def giveaway(interaction: discord.Interaction, time: int, prize: str):
    msg = await interaction.channel.send(f"🎉 Giveaway: {prize}\nReact 🎉 to join!")

    await msg.add_reaction("🎉")
    await interaction.response.send_message("✔ Giveaway started", ephemeral=True)

    await discord.utils.sleep_until(discord.utils.utcnow() + datetime.timedelta(seconds=time))

    new_msg = await interaction.channel.fetch_message(msg.id)
    users = await new_msg.reactions[0].users().flatten()
    users = [u for u in users if not u.bot]

    if users:
        winner = random.choice(users)
        await interaction.channel.send(f"🏆 Winner: {winner.mention}")
    else:
        await interaction.channel.send("❌ No participants")

# ---------------- ERROR HANDLER ---------------- #
@kick.error
@ban.error
@unban.error
@clear.error
@mute.error
@unmute.error
async def error_handler(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ You don’t have permission.", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ Error: {error}", ephemeral=True)

# ---------------- RUN ---------------- #
client.run(TOKEN)
