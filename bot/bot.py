import discord # import discord.py
from discord.ext import commands # import additional discord.py functionality
# import random
# import typing
import os # import the OS details, including our hidden bot token
# import asyncio
import asyncpg # import async/await postgres

dbName = None

## Connecting the DB ----------------------------------------------------------
async def run():
    global dbName
    
    dbURL = os.environ.get('DATABASE_URL')
    dbName = await asyncpg.connect(dsn=dbURL, ssl='require')
    
    await tarotdb.execute('''CREATE TABLE IF NOT EXISTS table (
                                id INTEGER PRIMARY KEY
                            );''')
    
## Bot Setup ----------------------------------------------------------
    
token = os.environ.get('DISCORD_BOT_TOKEN')

client = discord.Client()

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='prefix', intents=intents, dbName=dbName)

## Code Here ----------------------------------------------------------


## Bot Setup & Activation ----------------------------------------------------------
asyncio.get_event_loop().run_until_complete(run())
bot.run(token)
