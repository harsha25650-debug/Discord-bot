import discord
from discord.ext import commands
import asyncio
import datetime

TOKEN = os.getenv("TOKEN")

# ---------------- CONFIG ----------------
TOKEN = "YOUR_BOT_TOKEN"
DEFAULT_PREFIX = "!"

intents = discord.Intents.all()

# ---------------- PREFIX SYSTEM (per server) ----------------
prefixes = {}

def get_prefix(bot, message):
    return prefixes.get(message.guild.id, DEFAULT_PREFIX)

# ---------------- BOT ----------------
class NovaX(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=get_prefix,
            intents=intents
        )

    async def setup_hook(self):
        await self.tree.sync()
        print("Slash commands synced")

bot = NovaX()

# ---------------- CASE LOG SYSTEM ----------------
async def log_case(guild, text):
    channel = discord.utils.get(guild.text_channels, name="mod-logs")
    if channel:
        await channel.send(text)

# ---------------- READY ----------------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# ---------------- ERROR HANDLER (ZEP STYLE) ----------------
@bot.event
async def on_command_error(ctx, error):
    embed = discord.Embed(
        title="❌ Command Error",
        description=f"Error: `{str(error)}`\n\n"
                    "📌 Check command spelling\n"
                    "📌 Use !help to see correct commands\n"
                    "📌 Example: !ban @user reason",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

# ---------------- HELP PANEL ----------------
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📌 NovaX Help Panel",
        description="""
Moderation:
!ban, !unban, !kick, !mute, !unmute, !nick

Utility:
!say, !dm, !clear, !inviteinfo

System:
!prefix, !afk, !giveaway
""",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

# ---------------- MODERATION ----------------
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 Banned {member}")

    await log_case(ctx.guild, f"BAN | {member} | {reason}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"✅ Unbanned {user}")

    await log_case(ctx.guild, f"UNBAN | {user}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason"):
    await member.kick(reason=reason)
    await ctx.send(f"👢 Kicked {member}")

    await log_case(ctx.guild, f"KICK | {member} | {reason}")

# ---------------- MUTE / UNMUTE ----------------
@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, time: int = 10):
    await member.timeout(datetime.timedelta(minutes=time))
    await ctx.send(f"🔇 Muted {member} for {time} minutes")

    await log_case(ctx.guild, f"MUTE | {member} | {time} min")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member):
    await member.timeout(None)
    await ctx.send(f"🔊 Unmuted {member}")

    await log_case(ctx.guild, f"UNMUTE | {member}")

# ---------------- NICK CHANGE ----------------
@bot.command()
@commands.has_permissions(manage_nicknames=True)
async def nick(ctx, member: discord.Member, *, name):
    await member.edit(nick=name)
    await ctx.send(f"📝 Nick changed for {member}")

# ---------------- SAY ----------------
@bot.command()
async def say(ctx, *, msg):
    await ctx.message.delete()
    await ctx.send(msg)

# ---------------- DM COMMAND ----------------
@bot.command()
async def dm(ctx, member: discord.Member, *, msg):
    await member.send(msg)
    await ctx.send("📩 Message sent")

# ---------------- CLEAR ----------------
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Deleted {amount} messages", delete_after=3)

# ---------------- PREFIX CHANGE ----------------
@bot.command()
async def prefix(ctx, new_prefix):
    prefixes[ctx.guild.id] = new_prefix
    await ctx.send(f"⚙️ Prefix changed to `{new_prefix}`")

# ---------------- INVITE INFO ----------------
@bot.command()
async def inviteinfo(ctx):
    invites = await ctx.guild.invites()
    await ctx.send(f"🔗 Total invites: {len(invites)}")

# ---------------- AFK SYSTEM ----------------
afk_users = {}

@bot.command()
async def afk(ctx, *, reason="AFK"):
    afk_users[ctx.author.id] = reason
    await ctx.send(f"😴 You are AFK: {reason}")

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

# ---------------- GIVEAWAY (SIMPLE) ----------------
@bot.command()
async def giveaway(ctx, time: int, *, prize):
    msg = await ctx.send(f"🎉 Giveaway: {prize}\nReact 🎉 to join!")

    await msg.add_reaction("🎉")
    await asyncio.sleep(time)

    new_msg = await ctx.channel.fetch_message(msg.id)
    users = await new_msg.reactions[0].users().flatten()

    users = [u for u in users if not u.bot]

    if users:
        winner = random.choice(users)
        await ctx.send(f"🏆 Winner: {winner.mention}")
    else:
        await ctx.send("❌ No participants")

# ---------------- SLASH COMMAND EXAMPLE ----------------
@bot.tree.command(name="ping")
async def slash_ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

# ---------------- RUN ----------------
bot.run(TOKEN)
