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

timerSetupSQL = '''
    CREATE TABLE IF NOT EXISTS timers (
        id SERIAL UNIQUE,
        uid BIGINT,
        type TEXT,
        start TIMESTAMPTZ,
        duration TEXT,
        list INT[]
        );'''

timerCheckSQL = '''
    SELECT id FROM timers WHERE type = '00MASTER00';
    '''
    
timerMasterSQL = '''
    INSERT INTO timers (id,type,list) VALUES (0,'00MASTER00',$1);
    '''
 
## Connecting the DB ----------------------------------------------------------
async def run():
    global db
    
    dbURL = os.environ.get('DATABASE_URL')
    db = await asyncpg.connect(dsn=dbURL, ssl='require')
    
    await db.execute(masterSetupSQL)
    await db.execute(timerSetupSQL)
    
    emptyList = []
    
    timeCheck = await db.fetchval(timeCheckSQL)
    if timeCheck is None:
        await db.execute(timeMasterSQL)
    timerCheck = await db.fetchval(timerCheckSQL)
    if timerCheck is None:
        await db.execute(timerMasterSQL,emptyList)
    
## Bot Setup ----------------------------------------------------------
    
token = os.environ.get('DISCORD_BOT_TOKEN')
devID = int(os.environ.get('DEV_ID'))
testID = int(os.environ.get('TEST_CHANNEL'))
seasonID = int(os.environ.get('GH_DATE_CHANNEL'))
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
    bot.loop.create_task(timer_task())

async def season_task():
    while True:
        #seasonChannel = bot.get_channel(testID)
        seasonChannel = bot.get_channel(seasonID)
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
                wdDay = await db.fetchval('''SELECT day FROM master_table WHERE id = '00MASTER00';''')
                wdSeason = await db.fetchval('''SELECT season FROM master_table WHERE id = '00MASTER00';''')
                newName = str(wdSeason) + " " + str(wdDay)
                if seasonChannel.name != newName:
                    await seasonChannel.edit(reason=None,name=newName)
        await asyncio.sleep(300)

async def timer_task():
    await asyncio.sleep(30)
    while True:
        timerList = await db.fetchval('''SELECT list FROM timers WHERE type = '00MASTER00';''')
        now = datetime.datetime.now(datetime.timezone.utc)
        emptyList = []
        if timerList != emptyList:
            for y in timerList:
                startTime = await db.fetchval('''SELECT start FROM timers WHERE id = $1;''',y)
                duration = await db.fetchval('''SELECT duration FROM timers WHERE id = $1;''',y)
                hour, minutes = map(int, duration.split("h"))
                durationDelta = datetime.timedelta(hours=hour,minutes=minutes)
                timePassed = now - startTime
                if timePassed >= durationDelta:
                    user = await db.fetchval('''SELECT uid FROM timers WHERE id = $1;''',y)
                    timerType = await db.fetchval('''SELECT type FROM timers WHERE id = $1;''',y)
                    await dm_user(user, timerType)
                    await db.execute('''DELETE FROM timers WHERE id = $1;''',y)
        await asyncio.sleep(60)

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

@bot.group(aliases=["remind","r","timer"])
async def reminder(ctx):
    pass
    
async def dm_user(userID, type):
    user = await bot.fetch_user(userID)
    userDM = user.dm_channel
    mention = user.mention
    if userDM is None:
        try: # to create a DM channel
            userDM = await user.create_dm()
            await userDM.send("Your " + type + " is finished!")
        except: # not allowed, send in ctx
            await ctx.send(mention + " Your " + type + " is finished!")
    else:
        try: # to send in the pre-existing DM
            await userDM.send("Your " + type + " is finished!")
        except: # not allowed, send in ctx
            await ctx.send(mention + " Your " + type + " is finished!")
    
@reminder.command(aliases=["h","hunt"])
async def hunting(ctx):
    user = ctx.message.author
    await ctx.send("I'll remind you about your hunt in 30 minutes!")
    await asyncio.sleep(1800)
    await dm_user(user,"hunt")  
    
@reminder.command(aliases=["r","rescouting"])
async def rescout(ctx):
    user = ctx.message.author
    await ctx.send("I'll remind you about your rescout in 1 hour and 40 minutes!")
    await asyncio.sleep(6000)
    await dm_user(user,"rescout")
    
@reminder.command(aliases=["s","scouting"])
async def scout(ctx, type: typing.Optional[str]):
    user = ctx.message.author
    if type == "rescout":
        await ctx.send("I'll remind you about your rescout in 1 hour and 40 minutes!")
        await asyncio.sleep(6000)
        await dm_user(user,"rescout")
    else:
        duration = type
        if duration is None:
            await ctx.send("I'll remind you about your scout in 1 hour and 40 minutes!")
            await asyncio.sleep(6000)
            await dm_user(user,"scout")
        else:
            try:
                hour, minutes = map(int, duration.split("h"))
                if (hour > 1) or (hour >= 1 and minutes > 40):
                    await ctx.send("You can only set a reminder up to 1 hour and 40 minutes long.")
                    await ctx.command.reset_cooldown(ctx)
                else:
                    await ctx.send("I'll remind you about your scout in " + str(hour) + " hour and " + str(minutes) + " minutes!")
                    waitTime = hour * 60
                    waitTime += minutes
                    waitTime = waitTime * 60
                    await asyncio.sleep(waitTime)
                    await dm_user(user,"scout")
            except:
                await ctx.send("Please send in #h# format! Ex. `gh!scout 1h40` for 1 hour & 40 minutes.") 
                await ctx.command.reset_cooldown(ctx)
    
@reminder.command(aliases=["f"])
async def forage(ctx):
    user = ctx.message.author
    await ctx.send("I'll remind you about your forage in 1 hour!")
    await asyncio.sleep(3600)
    await dm_user(user,"forage")
    
@reminder.command(aliases=["m","med","mix"])
async def medicine(ctx, duration: typing.Optional[str]):
    if duration is None:
        await ctx.send("Please input the time as #h#. Eg. `gh!timer medicine 1h40` for 1 hour & 40 minutes.")
        await reminder.medicine.reset_cooldown(ctx)
    else:
        try:
            hour, minutes = map(int, duration.split("h"))
            if hour > 3:
                await ctx.send("You can only set a reminder up to 3 hours long.")
                await reminder.medicine.reset_cooldown(ctx)
            else:
                await ctx.send("I'll remind you about your medicine in " + str(hour) + " hour and " + str(minutes) + " minutes!")
                waitTime = hour * 60
                waitTime += minutes
                waitTime = waitTime * 60
                await asyncio.sleep(waitTime)
                await dm_user(user,"medicine")
        except:
            await ctx.send("Please input the time as #h#. Eg. `gh!timer medicine 1h40` for 1 hour & 40 minutes.")
            await reminder.medicine.reset_cooldown(ctx)

@hunting.error
async def hunt_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send("You already have a hunting reminder set. :cold_sweat:")
        
@scout.error
async def scout_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send("You already have max scouting reminders set. :cold_sweat:")
        
@medicine.error
async def medicine_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send("You already have a medicine reminder set. :cold_sweat:")
        
@forage.error
async def forage_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send("You already have a foraging reminders set. :cold_sweat:")


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
async def old_timer(ctx, minutes: int):
    user = ctx.message.author
    mention = ctx.message.author.mention
    seconds = minutes * 60
    await ctx.send("I'll remind you in " + str(minutes) + " minutes!")
    await asyncio.sleep(seconds)
    
@test.command()
@is_dev()
async def timer(ctx, duration: typing.Optional[str], timerType: str):
    user = ctx.message.author.id
    now = datetime.datetime.now(datetime.timezone.utc)
    await db.execute('''INSERT INTO timers (uid,type,start,duration) VALUES ($1,$2,$3,$4);''',user,timerType,now,duration)
    timerID = await db.fetchval('''SELECT id FROM timers WHERE start = $1;''',now)
    timersList = timerList = await db.fetchval('''SELECT list FROM timers WHERE type = '00MASTER00';''')
    timersList.append(timerID)
    await db.execute('''UPDATE timers SET list = $1 WHERE type = '00MASTER00';''',timersList)
    hour, minutes = map(int, duration.split("h"))
    if hour == 1:
        hourText = " hour "
    else:
        hourText = " hours "
    await ctx.send("I'll remind you in " + str(hour) + hourText + str(minutes) + " minutes!")
    
@set.command()
@is_dev()
async def typeFix(ctx):
   # await db.execute('''ALTER TABLE timers ALTER COLUMN start TYPE TIMESTAMP;''')
    #await ctx.send("Fix complete.")
    pass

@dev.group()
@is_dev()
async def delete(ctx):
    pass
    
@delete.command()
@is_dev()
async def timers(ctx):
    await db.execute('''DROP TABLE timers;''')
    await ctx.send("Fix complete.")
    
@dev.group()
@is_dev()
async def create(ctx):
    pass
    
    
    
## Bot Setup & Activation ----------------------------------------------------------
asyncio.get_event_loop().run_until_complete(run())
bot.run(token)
