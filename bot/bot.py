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
grouseID = int(os.environ.get('GH_GUILD'))
client = discord.Client()

bot = commands.Bot(command_prefix='gh!', db=db)

dayHours = [1,3,5,7,9,11,13,15,17,19,21,23]

biomeDict = {
    "Glacier": "Wisdom",
    "Tundra": "Smarts",
    "Tagia": "Agility",
    "Coniferous Forest": "Smarts",
    "Mountains": "Speed",
    "Grasslands": "Speed",
    "Deciduous Forest": "Speed",
    "Riparian Woodland": "Wisdom",
    "Prairie": "Speed",
    "Swamp": "Agility",
    "Rainforest": "Strength",
    "Desert": "Strength",
    "Glacier_Dif": "Challenging",
    "Tundra_Dif": "Challenging",
    "Tagia_Dif": "Difficult"
    "Coniferous Forest_Dif": "Medium",
    "Mountains_Dif": "Easy",
    "Grasslands_Dif": "Easy",
    "Deciduous Forest_Dif": "Easy",
    "Riparian Woodland_Dif": "Medium",
    "Prairie_Dif": "Medium",
    "Swamp_Dif": "Challenging",
    "Rainforest_Dif": "Challenging",
    "Desert_Dif": "Difficult"
}

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
                    timersList = await db.fetchval('''SELECT list FROM timers WHERE type = '00MASTER00';''')
                    timersList.remove(y)
                    await db.execute('''UPDATE timers SET list = $1 WHERE type = '00MASTER00';''',timersList)
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
    
async def set_timer(userID,timerType,duration):
    try:
        user = await bot.fetch_user(userID)
        name = user.name
    except:
        name = "error"
    try:
        grouseGuild = bot.get_guild(grouseID)
        guildMember = await grouseGuild.fetch_member(userID)
        displayName = guildMember.display_name
    except:
        displayName = "error"
    fullName = name + " | " + str(displayName)
    now = datetime.datetime.now(datetime.timezone.utc)
    await db.execute('''INSERT INTO timers (uid,username,type,start,duration) VALUES ($1,$2,$3,$4,$5);''',userID,fullName,timerType,now,duration)
    timerID = await db.fetchval('''SELECT id FROM timers WHERE start = $1;''',now)
    timersList = timerList = await db.fetchval('''SELECT list FROM timers WHERE type = '00MASTER00';''')
    timersList.append(timerID)
    await db.execute('''UPDATE timers SET list = $1 WHERE type = '00MASTER00';''',timersList)
    
@reminder.command(aliases=["h","hunt"])
async def hunting(ctx):
    user = ctx.message.author.id
    timerType = "hunt"
    duration = "0h30"
    await set_timer(user,timerType,duration)
    await ctx.send("I'll remind you about your hunt in 30 minutes!")
    
@reminder.command(aliases=["r","rescouting"])
async def rescout(ctx):
    user = ctx.message.author.id
    timerType = "rescout"
    duration = "1h40"
    await set_timer(user,timerType,duration)
    await ctx.send("I'll remind you about your rescout in 1 hour 40 minutes!")  
    
@reminder.command(aliases=["e","exploring","lead"])
async def explore(ctx):
    user = ctx.message.author.id
    timerType = "energy refill"
    duration = "1h15"
    await set_timer(user,timerType,duration)
    await ctx.send("I'll remind you about your energy refill in 1 hour 15 minutes!")
    
@reminder.command(aliases=["s","scouting"])
async def scout(ctx, type: typing.Optional[str]):
    user = ctx.message.author
    if type == "rescout":
        user = ctx.message.author.id
        timerType = "rescout"
        duration = "1h40"
        await set_timer(user,timerType,duration)
        await ctx.send("I'll remind you about your rescout in 1 hour 40 minutes!")
    else:
        duration = type
        if duration is None:
            user = ctx.message.author.id
            timerType = "scout"
            duration = "1h40"
            await set_timer(user,timerType,duration)
            await ctx.send("I'll remind you about your scout in 1 hour 40 minutes!")
        else:
            try:
                hour, minutes = map(int, duration.split("h"))
                if (hour > 1) or (hour >= 1 and minutes > 40):
                    await ctx.send("You can only set a reminder up to 1 hour and 40 minutes long.")
                else:
                    user = ctx.message.author.id
                    timerType = "scout"
                    await set_timer(user,timerType,duration)
                    if hour == 1:
                        hoursText = " hour "
                    else:
                        hoursText = " hours "
                    await ctx.send("I'll remind you about your scout in " + str(hour) + hoursText + str(minutes) + " minutes!")
            except:
                await ctx.send("Please send in #h# format! Ex. `gh!scout 1h40` for 1 hour & 40 minutes.") 
    
@reminder.command(aliases=["f"])
async def forage(ctx):
    user = ctx.message.author.id
    timerType = "forage"
    duration = "1h00"
    await set_timer(user,timerType,duration)
    await ctx.send("I'll remind you about your forage in 1 hour!")
    
@reminder.command(aliases=["m","med","mix"])
async def medicine(ctx, duration: typing.Optional[str]):
    if duration is None:
        await ctx.send("Please input the time as #h#. Eg. `gh!timer medicine 1h40` for 1 hour & 40 minutes.")
    else:
        try:
            hour, minutes = map(int, duration.split("h"))
            if hour > 3:
                await ctx.send("You can only set a reminder up to 3 hours long.")
            else:
                user = ctx.message.author.id
                timerType = "medicine"
                await set_timer(user,timerType,duration)
                if hour == 1:
                    hoursText = " hour "
                else:
                    hoursText = " hours "
                await ctx.send("I'll remind you about your medicine in " + str(hour) + hoursText + str(minutes) + " minutes!")
        except:
            await ctx.send("Please input the time as #h#. Eg. `gh!timer medicine 1h40` for 1 hour & 40 minutes.")

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

@bot.group()
async def lookup(ctx):
    pass
    
@lookup.command(aliases=["illness chart","illnesses chart"])
async def illnesses(ctx, illness: typing.Optional[int]):
    # TODO
    pass
    
@lookup.command(aliases=["herb table","herbs table"])
async def herbs(ctx, herb: typing.Optional[int]):
    # TODO
    pass
    
@lookup.command(aliases=["befriending chart"])
async def befriending(ctx, userInput: typing.Optional[int]):
    # TODO
    pass
    
@lookup.command(aliases=["personalities","personalities chart","personality chart"])
async def personality(ctx, userInput: typing.Optional[int]):
    # TODO
    pass
    
@lookup.command(aliases=["territory slots","territory slot","territory slot prices","territory prices"])
async def territory(ctx, slot: typing.Optional[int]):
    # TODO
    pass
    
@lookup.command(aliases=["biome stats","biome"])
async def biomes(ctx, biome: typing.Optional[int]):
    if biome is None:
        await ctx.send(file=discord.File("https://i.imgur.com/QZhyaVF.png"))
    elif biome in ["glacier","Glacier"]:
        biomeName = "Glacier"
    elif biome in ["tundra","Tundra"]:
        biomeName = "Tundra"
    elif biome in ["taiga","Taiga"]:
        biomeName = "Taiga"
    elif biome in ["coniferous forest","Coniferous forest","coniferous Forest","Coniferous Forest","Conf","conf"]:
        biomeName = "Coniferous Forest"
    elif biome in ["Mountains","mountains","Mountain","mountain"]:
        biomeName = "Mountains"
    elif biome in ["Grasslands","grasslands","Grassland","grassland"]:
        biomeName = "Grasslands"
    elif biome in ["deciduous Forest","deciduous forest","Deciduous Forest","Deciduous forest","decf","dec","Dec","Decf"]:
        biomeName = "Deciduous Forest"
    elif biome in ["riparian woodland","Riparian Woodland","riparian Woodland","Riparian woodland","riparian","Riparian","Rip","rip","Ripw","ripw","riparian woodlands","Riparian Woodlands","riparian Woodlands","Riparian woodlands","riprarian woodland","Riprarian Woodland","riprarian Woodland","Riprarian woodland","riparian","Riprarian","riprarian woodlands","Riprarian Woodlands","riprarian Woodlands","Riprarian woodlands"]:
        biomeName = "Riparian Woodland"
    elif biome in ["prairie","Prairie"]:
        biomeName = "Prairie"
    elif biome in ["swamp","Swamp"]:
        biomeName = "Swamp"
    elif biome in ["rainforest","Rainforest","rain forest","Rain forest","rain Forest","Rain Forest","rainf","Rainf"]:
        biomeName = "Rainforest"
    elif biome in ["desert","Desert","dessert","Dessert"]:
        biomeName = "Desert"
    else:
        biomeName = "Error"
    if biomeName == "Error":
        await ctx.send("I do not recognize biome name \"" + biome + "\".")
    else:
        biomeDifName = biomeName + "_Dif"
        await ctx.send(biomeName + " is *" + biomeDict[biomeDifName] + "* difficulty and uses the *" + biomeDict[biomeName] + "* stat.")
    
@lookup.command()
async def directory(ctx):
    linkEmbed = discord.Embed(title="Here's a quick link to the Grouse House Directory!", url="https://www.wolvden.com/chatter/topic/258")
    await ctx.send(embed=linkEmbed)
    await ctx.message.delete()


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
    
@get.command()
@is_dev()
async def id(ctx, userID: int):
    user = await bot.fetch_user(userID)
    name = user.name
    await ctx.send(name)
    grouseGuild = bot.get_guild(grouseID)
    guildMember = await grouseGuild.fetch_member(userID)
    displayName = guildMember.display_name
    await ctx.send(str(displayName))
    
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
async def all_timers(ctx):
    await db.execute('''DROP TABLE timers;''')
    await ctx.send("Fix complete.")
    
@delete.command()
@is_dev()
async def timer(ctx, timerID: int):
    await db.execute('''DELETE FROM timers WHERE id = $1;''',timerID)
    timersList = await db.fetchval('''SELECT list FROM timers WHERE type = '00MASTER00';''')
    timersList.remove(timerID)
    await db.execute('''UPDATE timers SET list = $1 WHERE type = '00MASTER00';''',timersList)
    await ctx.send("Timer deleted.")
    
@dev.group()
@is_dev()
async def create(ctx):
    pass
    
    
@create.command()
@is_dev()
async def column(ctx):
    await db.execute('''ALTER TABLE timers ADD COLUMN username TEXT;''')
    
    
## Bot Setup & Activation ----------------------------------------------------------
asyncio.get_event_loop().run_until_complete(run())
bot.run(token)
