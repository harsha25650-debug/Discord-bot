import discord
from discord.ext import commands
from discord import app_commands
import os
import datetime
import random

TOKEN = os.getenv("TOKEN")  # or paste token directly

# ---------------- INTENTS ---------------- #
intents = discord.Intents.all()

# ---------------- PREFIX SYSTEM ---------------- #
def get_prefix(bot, message):
    return "!"  # fixed prefix (!)

bot = commands.Bot(command_prefix=get_prefix, intents=intents)

tree = bot.tree

# ---------------- CASE LOG ---------------- #
async def log_case(guild, text):
    channel = discord.utils.get(guild.text_channels, name="mod-logs")
    if channel:
        await channel.send(f"📌 {text}")

# ---------------- READY ---------------- #
@bot.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {bot.user}")
    print("V2 PRO BOT ONLINE 🚀")

# ---------------- ERROR HANDLER ---------------- #
@bot.event
async def on_command_error(ctx, error):
    embed = discord.Embed(
        title="❌ Command Error",
        description=f"```{error}```\n\n"
                    "💡 Use !help for correct commands",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

# =================================================
#                PREFIX COMMANDS (!)
# =================================================

# ---------------- HELP ---------------- #
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📌 V2 PRO BOT HELP",
        description="""
**Moderation**
!ban !unban !kick !mute !unmute !clear

**Utility**
!say !dm !nick !invite

**System**
!afk !giveaway
        """,
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

# ---------------- SAY ---------------- #
@bot.command()
async def say(ctx, *, msg):
    await ctx.message.delete()
    await ctx.send(msg)

# ---------------- DM ---------------- #
@bot.command()
async def dm(ctx, member: discord.Member, *, msg):
    await member.send(msg)
    await ctx.send("✔ DM sent")

# ---------------- NICK ---------------- #
@bot.command()
@commands.has_permissions(manage_nicknames=True)
async def nick(ctx, member: discord.Member, *, name):
    await member.edit(nick=name)
    await ctx.send(f"✔ Nick changed for {member}")

# ---------------- INVITE INFO ---------------- #
@bot.command()
async def invite(ctx):
    invites = await ctx.guild.invites()
    await ctx.send(f"🔗 Total invites: {len(invites)}")

# ---------------- CLEAR ---------------- #
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Deleted {amount} messages", delete_after=3)

# ---------------- BAN ---------------- #
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 Banned {member}")
    await log_case(ctx.guild, f"BAN | {member} | {reason}")

# ---------------- UNBAN ---------------- #
@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"✔ Unbanned {user}")
    await log_case(ctx.guild, f"UNBAN | {user}")

# ---------------- KICK ---------------- #
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason"):
    await member.kick(reason=reason)
    await ctx.send(f"👢 Kicked {member}")
    await log_case(ctx.guild, f"KICK | {member} | {reason}")

# ---------------- MUTE ---------------- #
@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, minutes: int):
    until = datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes)
    await member.timeout(until)
    await ctx.send(f"🔇 Muted {member} for {minutes} min")
    await log_case(ctx.guild, f"MUTE | {member} | {minutes} min")

# ---------------- UNMUTE ---------------- #
@bot.command()
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member):
    await member.timeout(None)
    await ctx.send(f"🔊 Unmuted {member}")
    await log_case(ctx.guild, f"UNMUTE | {member}")

# ---------------- AFK SYSTEM ---------------- #
afk_users = {}

@bot.command()
async def afk(ctx, *, reason="AFK"):
    afk_users[ctx.author.id] = reason
    await ctx.send(f"😴 You are now AFK: {reason}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # AFK return check
    if message.author.id in afk_users:
        afk_users.pop(message.author.id)
        await message.channel.send(f"👋 Welcome back {message.author}")

    # AFK mention check
    for user in message.mentions:
        if user.id in afk_users:
            await message.channel.send(f"😴 {user} is AFK: {afk_users[user.id]}")

    await bot.process_commands(message)

# ---------------- GIVEAWAY ---------------- #
@bot.command()
async def giveaway(ctx, time: int, *, prize):
    msg = await ctx.send(f"🎉 GIVEAWAY: {prize}\nReact 🎉 to join!")
    await msg.add_reaction("🎉")

    await discord.utils.sleep_until(discord.utils.utcnow() + datetime.timedelta(seconds=time))

    new_msg = await ctx.channel.fetch_message(msg.id)
    users = await new_msg.reactions[0].users().flatten()
    users = [u for u in users if not u.bot]

    if users:
        winner = random.choice(users)
        await ctx.send(f"🏆 Winner: {winner.mention}")
    else:
        await ctx.send("❌ No participants")

# =================================================
#                SLASH COMMANDS (/)
# =================================================

@tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

@tree.command(name="help", description="Slash help menu")
async def slash_help(interaction: discord.Interaction):
    await interaction.response.send_message("Use !help for full commands or slash ping works.")

# ---------------- RUN ---------------- #
bot.run(TOKEN)
