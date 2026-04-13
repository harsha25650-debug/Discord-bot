import discord
import os

intents = discord.Intents.default()
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
