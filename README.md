# Instructions
A template for loading a bot made in DiscordPy to Heroku including the Postgres add-on.

## 0. Table of Contents
1. Main References
2. Essential Commands
3. Repository Directory
4. Deployment Steps
5. Additional Information

## 1. Main References
* [Heroku database webUI](https://data.heroku.com/)
* [Postgresql Add-on Page](https://elements.heroku.com/addons/heroku-postgresql)
* [Discord Developer Portal](https://discord.com/developers/applications)

## 2. Essential Commands
### Matching user IDs to table IDs
```python
userID = ctx.author.id
tableID = await dbName.fetchval("SELECT * FROM table WHERE user_id = $1;", userID)

# check if the user has ever sent command before, if not, add them to our table
if tableID is None:
    await dbName.execute("INSERT INTO table(user_id) VALUES($1);", userID)
```

### Fetching a value
```python
# by name
pythonVar = await dbName.fetchval("SELECT column FROM table WHERE user_ID = $1;", userID)

# by column
pythonVar = await dbName.fetchval("SELECT * FROM table WHERE user_id = $1;", userID, column=1)
```

### Updating a value
```python
await dbName.execute("UPDATE table SET column = $1 WHERE user_id = $2;",newValue,userID)
```

### Pinging me when online
```python
hostChannelID = os.environ.get('HOST_CHANNEL')
kchilID = os.environ.get('CREATOR_ID')

@bot.event
async def on_ready():
    hostChannel = bot.get_channel(int(hostChannelID))
    kchil = bot.get_user(kchilID)
    kchilPing = kchil.mention
    await hostChannel.send(kchilPing + " I am online.")
```

### Random activities
```python
activitiesList = []
listeningList = []
watchingList = []
streamingList = []
playingList = []
activitiesList.extend(listeningList)
activitiesList.extend(watchingList)
activitiesList.extend(streamingList)
activitiesList.extend(playingList)
currentActivitiesList = []
currentActivitiesList.extend(activitiesList)

async def status_task():
    global activitiesList
    global currentActivitiesList
    global activityChoice
    global listeningList
    global watchingList
    global playingList
    global streamingList
    
    while True:
        activityChoice = random.choice(currentActivitiesList)
        currentActivitiesList.clear()
        currentActivitiesList.extend(activitiesList)
        currentActivitiesList.remove(activityChoice)
        # listening
        if activityChoice in listeningList:
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=activityChoice))
        # watching
        elif activityChoice in watchingList:
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=activityChoice))
        # streaming
        elif activityChoice in streamingList:
            await bot.change_presence(activity=discord.Streaming(name=activityChoice,url="url here"))
        # playing
        elif activityChoice in playingList:
            await bot.change_presence(activity=discord.Game(name=activityChoice)) 
        await asyncio.sleep(60)
        
    @bot.event
    async def on_ready():
        bot.loop.create_task(status_task())
```


## 3. Repository Directory
* bot (folder): the folder for the python files
  * bot.py (python file): the file for our python bot
* Procfile (file with **no extension**): the process file Heroku refers to when knowing what commands to run to start your bot
* README.md (markdown file): the readme
* requirements.txt (plain-text file): lists the package requirements for our bot
* runtime.txt (plain-text file): lists the buildpack requirements for our bot

## 4. Deployment Steps
1. Create Discord app
2. Create bot for our app
3. Set profile pic & name
4. Copy bot token
5. Create/login Heroku
6. Create new app
7. Install postgresql add-on
7. Configure environment variable(s)
8. Connect to GitHub
9. Select repository
10. Turn on auto-deployments
11. Manually deploy
12. Turn on worker dyno


## 5. Additional References

Postgresql free account limits:
* 10,000 rows/records
* Estimated downtime 4 hours/month
* 1 GB storage
* Maximum 50 schemas

Useful links:
* [Heroku's docs for Deploying Python and Django Apps on Heroku](https://devcenter.heroku.com/articles/deploying-python)
* [Heroku's Python Support docs](https://devcenter.heroku.com/categories/python-support)
* [Heroku's article "How Heroku Works"](https://devcenter.heroku.com/articles/how-heroku-works)
* [Heroku's guide for deploying Python apps](https://devcenter.heroku.com/articles/getting-started-with-python) *\*Note: these instructions are for CLI/Console deployment
* [Heroku CLI Package](https://devcenter.heroku.com/articles/getting-started-with-python#set-up)
* [Which versions of Python/PyPy Heroku supports](https://devcenter.heroku.com/articles/python-support#specifying-a-python-version)
* [Heroku's dynos](https://www.heroku.com/dynos)
* [Postgres Guidelines](https://devcenter.heroku.com/articles/heroku-postgres-plans)
* [PostgreSQL add-on](https://elements.heroku.com/addons/heroku-postgresql)
* [Heroku PostgreSQL](https://devcenter.heroku.com/articles/heroku-postgresql)
  * From the same article as above, [Connecting in Python](https://devcenter.heroku.com/articles/heroku-postgresql#connecting-in-python)
* Heroku's Postgres Backups](https://devcenter.heroku.com/articles/heroku-postgres-backups)
* [Connecting to Heroku Postgres Databases from outside Heroku](https://devcenter.heroku.com/articles/connecting-to-heroku-postgres-databases-from-outside-of-heroku)
* [Monitoring Heroku Postgres](https://devcenter.heroku.com/articles/monitoring-heroku-postgres)
* [Heroku's Python connection guide](https://devcenter.heroku.com/articles/python-concurrency-and-database-connections).
* [PgBouncer Configuration](https://devcenter.heroku.com/articles/best-practices-pgbouncer-configuration)
* [Postgres Over Plan Capacity](https://devcenter.heroku.com/articles/heroku-postgres-over-plan-capacity)
* [Heroku Postgres Database Tuning](https://devcenter.heroku.com/articles/heroku-postgres-database-tuning)
* [Connection Pooling for Heroku Postgres](https://devcenter.heroku.com/articles/postgres-connection-pooling)
* [Heroku PGBackups](https://devcenter.heroku.com/articles/heroku-postgres-backups)

Code examples and references:
* [jegfish's example database connection](https://gist.github.com/jegfish/cfc7b22e72426f5ced6f87caa6920fd6)
* [Discord.py connection Stack Overflow](https://stackoverflow.com/questions/64271688/my-discord-py-bot-always-loses-connection-to-my-mysql-database-on-heroku)
