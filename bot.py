import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True  # Enable if you need message content

bot = commands.Bot(command_prefix="!", intents=intents)

async def send_message(ctx, message):
    print("ping")
    if len(message) <= 2000:
        await ctx.send(message)
    else:
        chunks = [message[i:i + 2000] for i in range(0, len(message), 2000)]
        for chunk in chunks:
            await ctx.send(chunk)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} commands.')
    except Exception as e:
        print(f'Error syncing commands: {e}')

async def load_cogs():
    await bot.load_extension('cogs.timezones')
    await bot.load_extension('cogs.headcounter')
    await bot.load_extension('cogs.fun')

# Running the bot
async def main():
    async with bot:
        await load_cogs()
        await bot.start(BOT_TOKEN)

asyncio.run(main())
