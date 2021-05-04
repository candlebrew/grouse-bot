import discord
from discord.ext import commands
import datetime
import random
import typing
import os
import asyncio
import asyncpg

## https://discord.com/api/oauth2/authorize?client_id=838960211187859508&permissions=257104&scope=bot

db = None

masterSetupSQL = '''
    CREATE TABLE IF NOT EXISTS master_table (
        id TEXT,
        season TEXT,
        day INT,
        year INT,
        day_check INT
        );'''

timeCheckSQL = '''
    SELECT season FROM master_table WHERE id = '00MASTER00';
    '''

timeMasterSQL = '''
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
devID = int(os.environ.get('DEV_ID'))
client = discord.Client()

bot = commands.Bot(command_prefix='gh!', db=db)

dayHours = [1,3,5,7,9,11,13,15,17,19,21,23]

def is_dev():
    def predicate(ctx):
        return ctx.message.author.id == devID
    return commands.check(predicate)

## Code Here ----------------------------------------------------------
@bot.event
async def on_ready():
    bot.loop.create_task(season_task())

async def season_task():
    while True:
        lastDay = await db.fetchval('''SELECT day_check FROM master_table WHERE id = '00MASTER00';''')
        now = datetime.datetime.now()
        if now.hour >= 7:
            if now.day != lastDay:
                # set day forwrad by one
                newDayCheck = now.day
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
    tempHour = now.hour - 7
    if tempHour < 0:
        newHour = 24 + tempHour
    else:
        newHour = tempHour
    now = now.replace(hour=newHour)
    if timeType is None:
        await ctx.send("It is currently **" + now.strftime("%H:%M") + "** Wolvden Time.")
    if timeType in ["d","n","night","nighttime","nightime","daytime","day"]:
        if now.hour in dayHours:
            currentPhase = "daytime"
            nextPhase = "night"
        else:
            currentPhase = "nighttime"
            nextPhase = "day"
        minutesLeft = 60 - now.minute
        await ctx.send("It is currently " + currentPhase + ". **" + str(minutesLeft) + " minutes** until " + nextPhase + ".")
    if timeType in ["e","event"]:
        ## TODO how much time left
        pass
    if timeType in ["r","rollover"]:
        minutesLeft = 60 - now.minute
        hoursLeft = 24 - now.hour
        await ctx.send("**" + str(hoursLeft) + " hours " + str(minutesLeft) + " minutes** until rollover.")
    if timeType in ["season","s","year","y","date"]:
        ## TODO current wd day/time
        currentSeason = await db.fetchval('''SELECT season FROM master_table WHERE id = '00MASTER00';''')
        currentDay = await db.fetchval('''SELECT day FROM master_table WHERE id = '00MASTER00';''')
        currentYear = await db.fetchval('''SELECT year FROM master_table WHERE id = '00MASTER00';''')
        if timeType == "season":
            await ctx.send("It is currently **" + str(currentSeason) + "**.")
        elif timeType == "year":
            await ctx.send("It is currently **Year " + str(currentYear) + "**.")
        else:
            await ctx.send("It is day " + str(currentDay) + " of " + str(currentSeason) + " in Year " + str(currentYear) + ".")

@bot.group(aliases=["remind","r"])
async def reminder(ctx):
    pass
    
@reminder.command(aliases=["h","hunt"])
async def hunting(ctx):
    user = ctx.message.author
    mention = ctx.message.author.mention
    await ctx.send("I'll remind you about your hunt in 30 minutes!")
    await asyncio.sleep(1800)
    try:
        await bot.send_message(user, "Your hunt is finished!")
    except:
        await ctx.send(mention + " Your hunt is finished!")


## ADMIN/DEV COMMANDS -------------------------------------------------------
@bot.group()
async def dev(ctx):
    pass

@dev.group()
async def set(ctx):
    pass
    
@dev.group()
async def get(ctx):
    pass
    
@dev.group()
async def test(ctx):
    pass
    
@set.command()
@is_dev()
async def day(ctx, newDay: int):
    await db.execute("UPDATE master_table SET day = $1 WHERE id = '00MASTER00';",newDay)
    await ctx.send("Your new day has been set to " + str(newDay))
    
@set.command()
@is_dev()
async def daycheck(ctx, newDay: int):
    await db.execute("UPDATE master_table SET day_check = $1 WHERE id = '00MASTER00';",newDay)
    await ctx.send("Your new daycheck has been set to " + str(newDay))
    
@get.command()
@is_dev()
async def daycheck(ctx):
    dayCheckDay = await db.fetchval('''SELECT day_check FROM master_table WHERE id = '00MASTER00';''')
    await ctx.send("Daycheck: " + str(dayCheckDay))
    
@test.command()
@is_dev()
async def timer(ctx, minutes: int):
    user = ctx.message.author
    mention = ctx.message.author.mention
    seconds = minutes * 60
    await ctx.send("I'll remind you in " + str(minutes) + " minutes!")
    await asyncio.sleep(seconds)
    try:
        await client.send_message(user, "Here is your reminder!")
    except:
        await ctx.send(mention + " Here is your reminder!")

    
## Bot Setup & Activation ----------------------------------------------------------
asyncio.get_event_loop().run_until_complete(run())
bot.run(token)
