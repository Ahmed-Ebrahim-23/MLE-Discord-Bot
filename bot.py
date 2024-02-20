import discord
from discord import Embed
from discord.ext import tasks
from datetime import datetime, timedelta
import requests
import asyncio
from Contest import Contest
from User import User


handle_not_found_message = "Please identify your handle first"
def check_handle(username):
    data = open("Data.txt","r")
    for line in data.readlines():
        if line!=None:
            user,handle,points,problem = line.split()
            if user == username:
                return handle
    return handle_not_found_message

def run_discord_bot(TOKEN):
    client = discord.Client(intents=discord.Intents().all())
    tree = discord.app_commands.CommandTree(client) 
    
    #=======================================================================================================
    # Help command
    @tree.command(
        name = 'help',
        description= 'list of all commands'
    )
    async def help(interaction : discord.Integration):
        commands = tree.get_commands()
        help_text = ""
        for command in commands:
            help_text += f"`/{command.name}` \n{command.description}\n\n"
        embed=Embed(
            title= "list of all commands",
            color= 0xFF0000,
            description=help_text,
        )
        await interaction.response.send_message(embed=embed)

    #=======================================================================================================
    # Upcoming codeforces contests command
    @tree.command(
        name = 'cfupcomingcontests',
        description= 'get a list of Up Coming Contests'
    )
    async def cfupcomingcontests(interaction : discord.Integration):
        message = Contest.UpComing_Contests_CF()
        embed=Embed(
            title= "Upcoming Codeforces Contests",
            color= 0xFF0000,
            description=message,
        )
        await interaction.response.send_message(embed=embed)

    #=======================================================================================================
    # Upcoming contests command
    @tree.command(
        name = 'upcomingcontests',
        description= 'get a list of all Up Coming Contests'
    )
    async def upcomingcontests(interaction : discord.Integration):
        message = Contest.UpComing_Contests()
        embed=Embed(
            title= "Upcoming Codeforces Contests",
            color= 0xFF0000,
            description=message,
        )
        await interaction.response.send_message(embed=embed)

    #=======================================================================================================
    # handle identify command
    @tree.command(
        name = 'handleidentify',
        description= 'identify your handle to be able to use the bot'
    )
    async def handleidentify(interaction : discord.Integration , handle:str):
        username = str(interaction.user.name)
        file_handle = check_handle(username)
        if(file_handle != handle_not_found_message):
            await interaction.response.send_message("You are already identified your handle")
        else:
            message = User.add_handle(username,handle)
            await interaction.response.send_message(embed=message)

    #=======================================================================================================
    # Random problem command
    @tree.command(
        name = 'random',
        description= 'get a random problem and use `redeempoints` to get points'
    )
    async def random(interaction : discord.Integration,rate:str):
        username = str(interaction.user.name)
        file_handle = check_handle(username)
        if(file_handle == handle_not_found_message):
            await interaction.response.send_message(handle_not_found_message)
        else:
            await interaction.response.defer()
            message = User.Random_Problem(int(rate),file_handle)
            try:
                await interaction.followup.send(message)
            except Exception as e:
                print(e)

    #=======================================================================================================
    # redeempoints command
    @tree.command(
        name = 'redeempoints',
        description= 'solve a random problem then get points to compete in the `leaderboard`'
    )
    async def redeempoints(interaction : discord.Integration):
        username = str(interaction.user.name)
        file_handle = check_handle(username)
        if(file_handle == handle_not_found_message):
            await interaction.response.send_message(handle_not_found_message)
        else:
            await interaction.response.defer()
            message = User.Redeem_Points(file_handle)
            try:
                await interaction.followup.send(message)
            except Exception as e:
                print(e)

    #=======================================================================================================
    # leaderboard command
    @tree.command(
        name = 'leaderboard',
        description= 'table of all users and there points'
    )
    async def leaderboard(interaction : discord.Integration):
        await interaction.response.defer()
        message = User.leaderboard()
        try:
            await interaction.followup.send(message)
        except Exception as e:
            print(e)

    #=======================================================================================================
    # Plot rating command
    @tree.command(
        name = 'plotrating',
        description= 'a plot of your contests rating change graph'
    )
    async def plotrating(interaction : discord.Integration):
        username = str(interaction.user.name)
        file_handle = check_handle(username)
        if(file_handle == handle_not_found_message):
            await interaction.response.send_message(handle_not_found_message)
        else:
            await interaction.response.defer()
            user = User(file_handle)
            file_path = user.plot_Rating()
            try:
                await interaction.followup.send(file = discord.File(file_path))
            except Exception as e:
                print(e)

    #=======================================================================================================
    # Scatter plot command
    @tree.command(
        name = 'plotscatter',
        description= 'scatter plot of all your solved problems rating'
    )
    async def plotscatter(interaction : discord.Integration):
        username = str(interaction.user.name)
        file_handle = check_handle(username)
        if(file_handle == handle_not_found_message):
            await interaction.response.send_message(handle_not_found_message)
        else:
            await interaction.response.defer()
            user = User(file_handle)
            file_path = user.plot_Scatter()
            try:
                await interaction.followup.send(file = discord.File(file_path))
            except Exception as e:
                print(e)

    #=======================================================================================================
    # plot problems command
    @tree.command(
        name = 'plotproblems',
        description= 'plot of public Codeforces submission status (Accepted/WA)'
    )
    async def plotproblems(interaction : discord.Integration):
        username = str(interaction.user.name)
        file_handle = check_handle(username)
        if(file_handle == handle_not_found_message):
            await interaction.response.send_message(handle_not_found_message)
        else:
            await interaction.response.defer()
            user = User(file_handle)
            file_path = user.plot_problems()
            try:
                await interaction.followup.send(file = discord.File(file_path))
            except Exception as e:
                print(e)
    

    #=======================================================================================================
    # Sending Contest Reminders
    @tasks.loop(minutes=1)
    async def check_contest():
            channel = client.get_channel(1075421992032927764)
            url = 'https://codeforces.com/api/contest.list'
            response = requests.get(url)
            print("Status -> " + response.json()['status'])

            contests = response.json()['result']
            upcomingContests = []
            flag = False

            for contest in contests:
                if contest["phase"] == "BEFORE":
                        durationHours = str(int(contest["durationSeconds"]/(60*60)))
                        durationMinute = str(int(contest["durationSeconds"]/60%60))
                        if len(durationMinute)==1:
                            durationMinute = durationMinute*2
                        duration = str(durationHours+":"+durationMinute)

                        # Convert Unix timestamp to a datetime object
                        unix_timestamp = contest["startTimeSeconds"] 
                        normalFormat = datetime.utcfromtimestamp(unix_timestamp) + timedelta(hours=2)
                        
                        day_of_week = normalFormat.weekday()
                        day_name = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][day_of_week]

                        con = Contest(contest["id"],contest["name"],duration,normalFormat,day_name)
                        upcomingContests.append(con)
            upcomingContests.reverse()

            for contest in upcomingContests:
                before_contest = contest.startTime - datetime.utcnow()
                reminder_time = timedelta(hours=2)
                if timedelta(hours=0) <= before_contest <= reminder_time:
                    flag = True
                    # send_reminder
                    embed = Embed(
                        color=0x00FF00,
                        description= f"### [{contest.name}](<https://codeforces.com/contests/{contest.id}>)\n**Contest Duration** {contest.duration}\n**Starts at** {contest.day}, {contest.startTime.strftime('%d/%m/%Y %I:%M %p')}"
                    )
                    await channel.send(embed=embed)
                    await channel.send('### Contest start in ~ 2 hours \n@everyone')
                    print(before_contest)
                else:
                    print(False)
            if flag:
                await asyncio.sleep(10800)  # sleep for three hours

    @check_contest.before_loop
    async def before():
            await client.wait_until_ready()
            print("Finished waiting")

    #=======================================================================================================
    # debug code

    @client.event
    async def on_ready():
        await tree.sync()
        check_contest.start()
        print(f'{client.user} is now running')


    @client.event
    async def on_message(message):      
        if(message.author == client.user):
            return
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)
        print(f"{username} said: {user_message} in {channel}")  

    client.run(TOKEN)
