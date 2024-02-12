import discord
from discord import Embed
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
    # Upcoming contests command
    @tree.command(
        name = 'upcomingcontests',
        description= 'get a list of Up Coming Codeforces Contests'
    )
    async def upcomingcontests(interaction : discord.Integration):
        message = Contest.UpComing_Contests()
        embed=Embed(
            title= "Upcoming Contests",
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
    # debug code

    @client.event
    async def on_ready():
        await tree.sync()

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
