import discord
from discord.ext import commands
from discord import app_commands
import os
import datetime
import random

# ---------------- TOKEN (MANDATORY) ---------------- #
TOKEN = os.getenv("TOKEN")

# ---------------- INTENTS ---------------- #
intents = discord.Intents.all()

# ---------------- BOT ---------------- #
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ---------------- CASE LOG ---------------- #
async def log_case(guild, text):
    if not guild:
        return

    channel = discord.utils.get(guild.text_channels, name="mod-logs")
    if channel:
        await channel.send(f"📌 {text}")

# ---------------- READY ---------------- #
@bot.event
async def on_ready():
    try:
        await tree.sync()
        print(f"Logged in as {bot.user}")
        print("Slash + Prefix bot ready 🚀")
    except Exception as e:
        print("Sync error:", e)

# ---------------- ERROR HANDLER ---------------- #
@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"❌ Error: `{error}`\nUse `!help`")

# =================================================
#                PREFIX COMMANDS (!)
# =================================================

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

@bot.command()
async def say(ctx, *, msg):
    await ctx.message.delete()
    await ctx.send(msg)

@bot.command()
async def dm(ctx, member: discord.Member, *, msg):
    try:
        await member.send(msg)
        await ctx.send("✔ DM sent")
    except:
        await ctx.send("❌ Cannot DM this user")

@bot.command()
async def nick(ctx, member: discord.Member, *, name):
    await member.edit(nick=name)
    await ctx.send(f"✔ Nick changed for {member}")

@bot.command()
async def clear(ctx, amount: int):
    if amount <= 0:
        return await ctx.send("❌ Invalid number")

    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Deleted {amount} messages", delete_after=3)

@bot.command()
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 Banned {member}")
    await log_case(ctx.guild, f"BAN | {member} | {reason}")

@bot.command()
async def unban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"✔ Unbanned {user}")
    await log_case(ctx.guild, f"UNBAN | {user}")

@bot.command()
async def kick(ctx, member: discord.Member, *, reason="No reason"):
    await member.kick(reason=reason)
    await ctx.send(f"👢 Kicked {member}")
    await log_case(ctx.guild, f"KICK | {member} | {reason}")

@bot.command()
async def mute(ctx, member: discord.Member, minutes: int):
    until = discord.utils.utcnow() + datetime.timedelta(minutes=minutes)
    await member.timeout(until)
    await ctx.send(f"🔇 Muted {member} for {minutes} min")
    await log_case(ctx.guild, f"MUTE | {member} | {minutes}")

@bot.command()
async def unmute(ctx, member: discord.Member):
    await member.timeout(None)
    await ctx.send(f"🔊 Unmuted {member}")
    await log_case(ctx.guild, f"UNMUTE | {member}")

# ---------------- AFK ---------------- #
afk_users = {}

@bot.command()
async def afk(ctx, *, reason="AFK"):
    afk_users[ctx.author.id] = reason
    await ctx.send(f"😴 AFK set: {reason}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.author.id in afk_users:
        afk_users.pop(message.author.id)
        await message.channel.send(f"👋 Welcome back {message.author}")

    for user in message.mentions:
        if user.id in afk_users:
            await message.channel.send(f"😴 {user} is AFK: {afk_users[user.id]}")

    await bot.process_commands(message)

# ---------------- GIVEAWAY (FIXED) ---------------- #
@bot.command()
async def giveaway(ctx, time: int, *, prize):
    msg = await ctx.send(f"🎉 GIVEAWAY: {prize}\nReact 🎉")

    await msg.add_reaction("🎉")

    await discord.utils.sleep_until(discord.utils.utcnow() + datetime.timedelta(seconds=time))

    try:
        new_msg = await ctx.channel.fetch_message(msg.id)
        users = await new_msg.reactions[0].users().flatten()
        users = [u for u in users if not u.bot]

        if users:
            winner = random.choice(users)
            await ctx.send(f"🏆 Winner: {winner.mention}")
        else:
            await ctx.send("❌ No participants")
    except:
        await ctx.send("❌ Giveaway error")

# =================================================
#                SLASH COMMANDS (/)
# =================================================

@tree.command(name="ping", description="Check bot")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

# ---------------- RUN ---------------- #
if TOKEN is None:
    print("❌ TOKEN not found in environment variables")
else:
    bot.run(TOKEN)
