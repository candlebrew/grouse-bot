import discord
from discord.ext import commands
import datetime
import random
import typing
import os
import asyncio
import asyncpg
import io
import aiohttp

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
    "Taiga": "Agility",
    "Coniferous Forest": "Smarts",
    "Mountains": "Speed",
    "Grasslands": "Speed",
    "Deciduous Forest": "Speed",
    "Riparian Woodland": "Wisdom",
    "Prairie": "Speed",
    "Swamp": "Agility",
    "Rainforest": "Strength",
    "Desert": "Strength",
    "Glacier_Dif": "challenging",
    "Tundra_Dif": "challenging",
    "Taiga_Dif": "difficult",
    "Coniferous Forest_Dif": "medium",
    "Mountains_Dif": "easy",
    "Grasslands_Dif": "easy",
    "Deciduous Forest_Dif": "easy",
    "Riparian Woodland_Dif": "medium",
    "Prairie_Dif": "medium",
    "Swamp_Dif": "challenging",
    "Rainforest_Dif": "challenging",
    "Desert_Dif": "difficult"
    }

slotsDict = {
    1: "Free (starter)",
    2: "Free (starter)",
    3: "Free (unlocked after \"Pack Life\" Quest)",
    4: "Free (unlocked after \"Pack Life\" Quest)",
    5: "Free (unlocked after \"A Step in the Right Direction\" achievement, or 105 SC if purchased before achievement.)",
    6: "130 SC",
    7: "155 SC",
    8: "180 SC",
    9: "205 SC",
    10: "230 SC",
    11: "255 SC",
    12: "280 SC",
    13: "305 SC",
    14: "330 SC",
    15: "355 SC",
    16: "380 SC",
    17: "405 SC",
    18: "430 SC",
    19: "455 SC",
    20: "480 SC",
    21: "505 SC",
    22: "530 SC",
    23: "555 SC",
    24: "580 SC",
    25: "605 SC",
    26: "630 SC",
    27: "655 SC",
    28: "680 SC",
    29: "705 SC",
    30: "730 SC",
    31: "755 SC",
    32: "780 SC",
    33: "805 SC",
    34: "830 SC",
    35: "855 SC",
    36: "880 SC",
    37: "905 SC",
    38: "930 SC",
    39: "955 SC",
    40: "980 SC",
    41: "1005 SC",
    42: "1030 SC",
    43: "1055 SC",
    44: "1080 SC",
    45: "1105 SC",
    46: "1130 SC",
    47: "1155 SC",
    48: "1180 SC",
    49: "1205 SC",
    50: "1230 SC",
    51: "1255 SC",
    52: "2 GC",
    53: "2 GC",
    54: "2 GC",
    55: "2 GC",
    56: "2 GC",
    57: "2 GC",
    58: "2 GC",
    59: "2 GC",
    60: "2 GC",
    61: "2 GC",
    62: "3 GC",
    63: "3 GC",
    64: "3 GC",
    65: "3 GC",
    66: "3 GC",
    67: "3 GC",
    68: "3 GC",
    69: "3 GC",
    70: "3 GC",
    71: "3 GC",
    72: "3 GC",
    73: "3 GC",
    74: "3 GC",
    75: "3 GC",
    76: "3 GC",
    77: "3 GC",
    78: "3 GC",
    79: "3 GC",
    80: "3 GC",
    81: "3 GC",
    82: "4 GC",
    83: "4 GC",
    84: "4 GC",
    85: "4 GC",
    86: "4 GC",
    87: "4 GC",
    88: "4 GC",
    89: "4 GC",
    90: "4 GC",
    91: "4 GC",
    92: "4 GC",
    93: "4 GC",
    94: "4 GC",
    95: "4 GC",
    96: "4 GC",
    97: "4 GC",
    98: "4 GC",
    99: "4 GC",
    100: "4 GC",
    101: "4 GC",
    102: "5 GC",
    103: "5 GC",
    104: "5 GC",
    105: "5 GC",
    106: "5 GC",
    107: "5 GC",
    108: "5 GC",
    109: "5 GC",
    110: "5 GC",
    111: "5 GC",
    112: "5 GC",
    113: "5 GC",
    114: "5 GC",
    115: "5 GC",
    116: "5 GC",
    117: "5 GC",
    118: "5 GC",
    119: "5 GC",
    120: "5 GC",
    121: "5 GC",
    122: "6 GC",
    123: "6 GC",
    124: "6 GC",
    125: "6 GC",
    126: "6 GC",
    127: "6 GC",
    128: "6 GC",
    129: "6 GC",
    130: "6 GC",
    131: "6 GC",
    132: "6 GC",
    133: "6 GC",
    134: "6 GC",
    135: "6 GC",
    136: "6 GC",
    137: "6 GC",
    138: "6 GC",
    139: "6 GC",
    140: "6 GC",
    141: "6 GC",
    142: "7 GC",
    143: "7 GC",
    144: "7 GC",
    145: "7 GC",
    146: "7 GC",
    147: "7 GC",
    148: "7 GC",
    149: "7 GC",
    150: "7 GC",
    151: "7 GC",
    152: "7 GC",
    153: "7 GC",
    154: "7 GC",
    155: "7 GC",
    156: "7 GC",
    157: "7 GC",
    158: "7 GC",
    159: "7 GC",
    160: "7 GC",
    161: "7 GC",
    162: "8 GC",
    163: "8 GC",
    164: "8 GC",
    165: "8 GC",
    166: "8 GC",
    167: "8 GC",
    168: "8 GC",
    169: "8 GC",
    170: "8 GC",
    181: "8 GC",
    182: "9 GC",
    183: "9 GC",
    184: "9 GC",
    185: "9 GC",
    186: "9 GC",
    187: "9 GC",
    188: "9 GC",
    189: "9 GC",
    190: "9 GC",
    191: "9 GC",
    192: "9 GC",
    193: "9 GC",
    194: "9 GC",
    195: "9 GC",
    196: "9 GC",
    197: "9 GC",
    198: "9 GC",
    199: "9 GC",
    200: "9 GC"
    }

aggressiveList = [
    "Arrogant","Bossy","Combative","Conceited","Impulsive","Malicious","Obnoxious","Sarcastic","Selfish","Vulgar"]
friendlyList = [
    "Adventurous","Amiable","Fair","Helpful","Humble","Lazy","Observant","Optimistic","Scatterbrained","Sociable"]
romanticList = [
    "Capable","Charming","Confident","Dedicated","Dutiful","Imaginative","Keen","Precise","Reliable","Trusting"]
stoicList = [
    "Aloof","Anxious","Dishonest","Independent","Neutral","Pessimistic","Quiet","Sneaky","Sullen","Unfriendly"]
dispositionsList = [
    "Aggressive","Friendly","Romantic","Stoic"]
personalitiesList = []
personalitiesList.extend(aggressiveList)
personalitiesList.extend(friendlyList)
personalitiesList.extend(romanticList)
personalitiesList.extend(stoicList)

herbsDict = {
    "aloe_uses": "Rich Healing Salve and Ringworm Salve",
    "arnica_uses": "Mange Salve",
    "bearberry_uses": "Constipation Cure and Tapeworm Remedy",
    "boneset_uses": "Hepatitis Cure",
    "buffaloberry_uses": "Constipation Cure and Rich Healing Salve",
    "burning bush_uses": "Constipation Cure and Rich Healing Salve",
    "carrionflower_uses": "Ear Mites Ointment",
    "cedar bark_uses": "Tick Remedy",
    "chaparral_uses": "Antidote and Rich Healing Salve",
    "charcoal_uses": "Diarrhea Cure, Healing Salve, and Rich Healing Salve",
    "dandelion_uses": "Cystitis Cure, Healing Salve, and Hepatitis Cure",
    "feverfew_uses": "Heatstroke Remedy and Infection Balm",
    "garlic_uses": "Tapeworm Remedy and Tick Remedy",
    "ginger_uses": "Heatstroke Remedy",
    "goldenseal_uses": "Cough Cure and Distemper Cure",
    "guaiacum_uses": "Distemper Cure and Influenza Cure",
    "kava_uses": "Cough Cure and Cystitis Cure",
    "mullein_uses": "Distemper Cure",
    "oregano_uses": "Infection Balm, Pox Balm, and Ringworm Salve",
    "pineapple leaf_uses": "Cough Cure and Influenza Cure",
    "redwood sorrel_uses": "Cystitis Cure and Pox Balm",
    "spoonwood_uses": "Hepatitis Cure",
    "st. john's wort_uses": "Infection Balm and Open Wound Salve",
    "st john's wort_uses": "Infection Balm and Open Wound Salve",
    "st. johns wort_uses": "Infection Balm and Open Wound Salve",
    "st johns wort_uses": "Infection Balm and Open Wound Salve",
    "tansy_uses": "Tapeworm Remedy",
    "tobacco_uses": "Ear Mites Ointment, Fleas Remedy, Mange Salve, and Tick Remedy",
    "turmeric_uses": "Ringworm Salve",
    "winterfat_uses": "Ear Mites Ointment, Heatstroke Remedy, and Open Wound Salve",
    "yarrow_uses": "Mange Salve, Open Wound Salve, and Pox Balm",
    "aloe_locations": "Desert, Swamp, and Rainforest",
    "arnica_locations": "All locations",
    "bearberry_locations": "Deciduous Forest, Mountains, Coniferous Forest, Taiga, and Tundra",
    "boneset_locations": "Deciduous Forest, Grasslands, Coniferous Forest, Prairie, Riparian Woodland, Taiga, and Swamp",
    "buffaloberry_locations": "Mountains, Coniferous Forest, Prairie, Riparian Woodland, and Taiga",
    "burning bush_locations": "Deciduous Forest, Grasslands, Coniferous Forest, Prairie, and Riparian Woodland",
    "carrionflower_locations": "Deciduous Forest, Grasslands, Mountains, Coniferous Forest, Riparian Woodland, and Taiga",
    "cedar bark_locations": "Deciduous Forest, Grasslands, Mountains, Coniferous Forest, Prairie, Riparian Woodland, Desert, Swamp, and Rainforest",
    "chaparral_locations": "Desert",
    "charcoal_locations": "All" ,
    "dandelion_locations": "All",
    "feverfew_locations": "Deciduous Forest, Grasslands, Mountains, Coniferous Forest, Prairie, Riparian Woodland, and Rainforest",
    "garlic_locations": "Deciduous Forest, Grasslands, Mountains, Coniferous Forest, Prairie, Riparian Woodland, and Swamp",
    "ginger_locations": "Deciduous Forest, Grasslands, Mountains, Coniferous Forest, Prairie, Riparian Woodland, and Taiga",
    "goldenseal_locations": "Deciduous Forest, Grasslands, Coniferous Forest, and Riparian Woodland.",
    "guaiacum_locations": "Swamp and Rainforest",
    "kava_locations": "Rainforest",
    "mullein_locations": "Deciduous Forest, Grasslands, Mountains, Coniferous Forest, Prairie, Riparian Woodland, and Desert",
    "oregano_locations": "Mountains, Prairie, Desert, Swamp, and Rainforest",
    "pineapple leaf_locations": "Rainforest",
    "redwood sorrel_locations": "Mountains, Coniferous Forest, and Swamp",
    "spoonwood_locations": "Deciduous Forest, Grasslands, Mountains, Coniferous Forest, Riparian Woodland, and Swamp",
    "st. john's wort_locations": "Deciduous Forest, Grasslands, Mountains, Coniferous Forest, Prairie, Riparian Woodland, and Swamp",
    "st john's wort_locations": "Deciduous Forest, Grasslands, Mountains, Coniferous Forest, Prairie, Riparian Woodland, and Swamp",
    "st. johns wort_locations": "Deciduous Forest, Grasslands, Mountains, Coniferous Forest, Prairie, Riparian Woodland, and Swamp",
    "st johns wort_locations": "Deciduous Forest, Grasslands, Mountains, Coniferous Forest, Prairie, Riparian Woodland, and Swamp",
    "tansy_locations": "Deciduous Forest, Grasslands, Mountains, Coniferous Forest, Prairie, Riparian Woodland, and Desert",
    "tobacco_locations": "Mountains, Prairie, and Desert",
    "turmeric_locations": "Swamp and Rainforest",
    "winterfat_locations": "Mountains, Prairie, and Desert",
    "yarrow_locations": "All"
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
    
@lookup.command(aliases=["illness"])
async def illnesses(ctx, illness: typing.Optional[int]):
    # TODO
    pass
    
@lookup.command(aliases=["herb"])
async def herbs(ctx, *, herb: typing.Optional[str]):
    if herb is None:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://i.imgur.com/eSJtHvh.png") as resp:
                if resp.status != 200:
                    return await ctx.send('Could not download file...')
                data = io.BytesIO(await resp.read())
                await ctx.send(file=discord.File(data, "herbs_image.png"))
    else:
        try:
            herbUses = herb + "_uses"
            herbBiomes = herb + "_locations"
            await ctx.send("Used for: *" + herbsDict[herbUses] + "*\nFound in the following biomes: *" + herbsDict[herbBiomes]) +"*"
        except:
            await ctx.send("I was unable to find information about that herb. :worried: Try checking your spelling.")
    
@lookup.command(aliases=["befriend"])
async def befriending(ctx, disposition: typing.Optional[str]):
    if disposition is None:
        imageURL = "https://i.imgur.com/VfxzuxG.png"
        imageName = "befriending_image.png"
    else:
        if disposition in ["Aggressive","aggressive"]:
            imageURL = "https://i.imgur.com/qFIP743.png"
            imageName = "befriending_aggressive_image.png"
        elif disposition in ["Friendly","friendly"]:
            imageURL = "https://i.imgur.com/U3CGvIU.png"
            imageName = "befriending_friendly_image.png"
        elif disposition in ["Romantic","romantic"]:
            imageURL = "https://i.imgur.com/orjiyC9.png"
            imageName = "befriending_romantic_image.png"
        elif disposition in ["Stoic","stoic"]:
            imageURL = "https://i.imgur.com/e6CFl5m.png"
            imageName = "befriending_stoic_image.png"
        else:
            imageName = "Error"
    if imageName == "Error":
            await ctx.send("I do not recognize " + disposition + " as a valid disposition.")
    else:
        async with aiohttp.ClientSession() as session:
            async with session.get(imageURL) as resp:
                if resp.status != 200:
                    return await ctx.send('Could not download file...')
                data = io.BytesIO(await resp.read())
                await ctx.send(file=discord.File(data, imageName))
    
@lookup.command(aliases=["personalities"])
async def personality(ctx, userInput: typing.Optional[str]):
    if userInput is None:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://i.imgur.com/ewtlsRM.png") as resp:
                if resp.status != 200:
                    return await ctx.send('Could not download file...')
                data = io.BytesIO(await resp.read())
                await ctx.send(file=discord.File(data, "personalities_image.png"))
    else:
        if userInput.capitalize() in personalitiesList:
            if userInput.capitalize() in aggressiveList:
                disposition = "**Aggressive**"
                fightDisposition = "**Friendly**"
            elif userInput.capitalize() in friendlyList:
                disposition = "**Friendly**"
                fightDisposition = "**Aggressive**"
            elif userInput.capitalize() in romanticList:
                disposition = "**Romantic**"
                fightDisposition = "**Stoic**"
            elif userInput.capitalize() in stoicList:
                disposition = "**Stoic**"
                fightDisposition = "**Romantic**"
            await ctx.send(userInput.capitalize() + " is a " + disposition + " personality type. It will fight with " + fightDisposition + " personality types.")
        elif userInput.capitalize() in dispositionsList:
            if userInput.capitalize() == "Aggressive":
                listForLoop = aggressiveList
                fightDisposition = "**Friendly**"
            elif userInput.capitalize() == "Friendly":
                listForLoop = friendlyList
                fightDisposition = "**Aggressive**"
            elif userInput.capitalize() == "Romantic":
                listForLoop = romanticList
                fightDisposition = "**Stoic**"
            elif userInput.capitalize() == "Stoic":
                listForLoop = stoicList
                fightDisposition = "**Romantic**"
            message = "**" + userInput.capitalize() + "** fights with " + fightDisposition + " personalities.\n" + "*"
            for i in listForLoop:
                if i not in ["Vulgar","Sociable","Trusting","Unfriendly"]:
                    message += i + ", "
                else:
                    message += i + "*"
            await ctx.send(message)
        else:
            await ctx.send("I do not recognize " + userInput + " as a valid personality or disposition.")
    
@lookup.command(aliases=["slot","slots"])
async def territory(ctx, slot: typing.Optional[int]):
    if slot is None:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://i.imgur.com/ayl0eHx.jpg") as resp:
                if resp.status != 200:
                    return await ctx.send('Could not download file...')
                data = io.BytesIO(await resp.read())
                await ctx.send(file=discord.File(data, "slots_image.png"))
    else:
        if (slot < 1) or (slot > 200):
            await ctx.send("Please list a slot between 1-200.")
        else:
            await ctx.send("Slot " + str(slot) + ": " + slotsDict[slot])

@lookup.command(aliases=["biome"])
async def biomes(ctx, biome: typing.Optional[str]):
    if biome is None:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://i.imgur.com/QZhyaVF.png") as resp:
                if resp.status != 200:
                    return await ctx.send('Could not download file...')
                data = io.BytesIO(await resp.read())
                await ctx.send(file=discord.File(data, "biome_image.png"))
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
    
@bot.command()
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
