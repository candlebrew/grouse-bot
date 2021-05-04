import discord
from discord.ext import commands
import datetime
import random
import typing
import os
import asyncio
import asyncpg

## https://discord.com/api/oauth2/authorize?client_id=838960211187859508&permissions=117824&scope=bot

db = None

masterSetupSQL = 
'''CREATE TABLE IF NOT EXISTS master_table (
    id TEXT,
    season TEXT,
    day INT,
    year INT,
    day_check INT
    );'''

timeCheckSQL = 
'''
SELECT season FROM master_table WHERE id = '00MASTER00';
'''

timeMasterSQL = 
'''
INSERT INTO master_table (id,season,day,year,day_check) VALUES ('00MASTER00','Spring',4,5,4);
'''

## Connecting the DB ----------------------------------------------------------
async def run():
    global db
    
    dbURL = os.environ.get('DATABASE_URL')
    db = await asyncpg.connect(dsn=dbURL, ssl='require')
    
    await db.execute(masterSetupSQL)
    
    timeCheck = await db.fetchval(timeCheckSQL)
    if timeCheck is None:
        await db.execute(timeMasterSQL)
    
## Bot Setup ----------------------------------------------------------
    
token = os.environ.get('DISCORD_BOT_TOKEN')
client = discord.Client()

bot = commands.Bot(command_prefix='gh!', db=db)

dayHours = [1,3,5,7,9,11,13,15,17,19,21,23]

## Code Here ----------------------------------------------------------
@bot.event
async def on_ready():
    bot.loop.create_task(season_task())


async def season_task():
    while True:
        lastDay = await db.fetchval('''SELECT day_check FROM master_table WHERE id = '00MASTER00';''')
        now = datetime.datetime.now()
        if now.Hour == 7:
            if now.Day != lastDay:
                # set day forwrad by one
                newDayCheck = now.Day
                oldDay = await db.fetchval('''SELECT day FROM master_table WHERE id = '00MASTER00';''')
                oldSeason = await db.fetchval('''SELECT season FROM master_table WHERE id = '00MASTER00';''')
                oldYear = await db.fetchval('''SELECT year FROM master_table WHERE id = '00MASTER00';''')
                newDay = oldDay + 1
                if newDay == 7:
                    newDay = 1
                    if oldSeason in ["Spring","Summer","Autumn"]:
                        newYear = oldYear
                    if oldSeason == "Spring":
                        newSeason = "Summer"
                    elif oldSeason == "Summer":
                        newSeason = "Autumn"
                    elif oldSeason == "Autumn":
                        newSeason = "Winter"
                    elif oldSeason == "Winter":
                        newSeason = "Spring"
                        newYear = oldYear + 1
                else:
                    newSeason = oldSeason
                    newYear = oldYear
                await db.execute("UPDATE master_table SET day = $1 WHERE id = '00MASTER00';",newDay)
                await db.execute("UPDATE master_table SET season = $1 WHERE id = '00MASTER00';",newSeason)
                await db.execute("UPDATE master_table SET year = $1 WHERE id = '00MASTER00';",newYear)
                await db.execute("UPDATE master_table SET day_check = $1 WHERE id = '00MASTER00';",newDayCheck)
        await asyncio.sleep(300)

@bot.command(alisaes=["t"])
async def time(ctx, timeType: typing.Optional[str]):
    now = datetime.datetime.now()
    tempHour = now.Hour - 7
    if tempHour < 0:
        newHour = 24 + tempHour
    else:
        newHour = tempHour
    now = now.replace(hour=newHour)
    if timeType is None:
        await ctx.send("It is currently **" + now.strftime("%H:%M") + "** Wolvden Time.")
    if timeType in ["d","n","night","nighttime","nightime","daytime","day"]:
        if now.Hour in dayHours:
            currentPhase = "daytime"
            nextPhase = "night"
        else:
            currentPhase = "nighttime"
            nextPhase = "day"
        minutesLeft = 60 - now.Minute
        await ctx.send("It is currently " + currentPhase + ". **" + str(minutesLeft) + " minutes** until " + nextPhase + ".")
    if timeType in ["e","event"]:
        ## TODO how much time left
        pass
    if timeType in ["r","rollover"]:
        minutesLeft = 60 - now.Minute
        hoursLeft = 24 - now.Hour
        await ctx.send("**" + str(hoursLeft) + " hours " + str(minutesLeft) + " minutes** until rollover.")
    if timeType in ["season","s","year","y"]:
        ## TODO current wd day/time
        currentSeason = await db.fetchval('''SELECT season FROM master_table WHERE id = '00MASTER00';''')
        currentDay = await db.fetchval('''SELECT day FROM master_table WHERE id = '00MASTER00';''')
        currentYear = await db.fetchval('''SELECT year FROM master_table WHERE id = '00MASTER00';''')
        await ctx.send("It is day " + str(currentDay) + " of " + str(currentSeason) + " in Year " + str(currentYear) + ".")

## Bot Setup & Activation ----------------------------------------------------------
asyncio.get_event_loop().run_until_complete(run())
bot.run(token)
