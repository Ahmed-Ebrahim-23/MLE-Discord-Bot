from discord import Embed
import os
import requests
import matplotlib.pyplot as plt
import random
from PIL import Image

class User:
    def __init__(self,handle):
        self.handle = handle 

    def add_handle(username,handle):
        url = f'https://codeforces.com/api/user.info?handles={handle}'
        response = requests.get(url)
        print("Status -> " + response.json()['status'])

        rankcolors = {"newbie": 0x808080,"pupil": 0x028000, "specialist": 0x03A89E , 
              "expert": 0x0000FF, "candidate master": 0xAA00AA,"master": 0xFF8C00, "international master": 0xFF8C00,
              "grandmaster": 0xFF0000,"international grandmaster": 0xFF0000, "legendary grandmaster": 0xFF0000}

        profile = response.json()['result'][0]
        embed = Embed()

        if(response.json()['status'] == "FAILED"):
            embed.description = f"User with handle `{handle}` not found"
        else:
            data = open('Data.txt','a')
            data.write(f'{username} {handle} 0 NULL\n')
            embed.description = f"Handle set to [{handle}](https://codeforces.com/profile/{handle})\n\n**Rate:** {profile['rating']}\n\n**Rank:** {profile['rank']}"
            embed.set_thumbnail(url=profile["avatar"])
            embed.color = rankcolors[profile['rank']]

        return embed

    def plot_Rating(self):
        url = f'https://codeforces.com/api/user.rating?handle={self.handle}'
        response = requests.get(url)
        print("Status -> " + response.json()['status'])

        contests = response.json()['result']

        rating = []
        plot = []
        maxRate = 0
        x=0
        for contest in contests:
            if x==0:
                x = contest['ratingUpdateTimeSeconds']/(60*60*24)
            maxRate=max(maxRate,int(contest['newRating']))
            rating.append(int(contest['newRating']))
            plot.append(int(contest['ratingUpdateTimeSeconds']/(60*60*24)-x))

        # Plotting the lists

        fig, ax = plt.subplots()
        y_points = [0,1200,1400,1600,1900,2100,2300,2400,2600,3000,4000]
        color = ['lightgray','limegreen','turquoise','royalblue','magenta','moccasin','orange','lightcoral','red','maroon']

        ax.plot(plot,rating,label = self.handle, marker='o' , ms=5 , mfc ='w', linestyle='-', color='gold')

        i=0
        for c in color:
            ax.axhspan(ymin=y_points[i], ymax=y_points[i+1], facecolor=c, alpha=0.6)
            i+=1
            if(y_points[i]>maxRate):
                break

        ax.set_xticks([])
        ax.set_yticks(y_points[:i+1])
        ax.legend()


        plt.savefig(fname='plotrating')
        image = Image.open("plotrating.png")
        return os.path.abspath(image.filename)
    
    def plot_Scatter(self):
        url = f'https://codeforces.com/api/user.status?handle={self.handle}'
        response = requests.get(url)
        print("Status -> " + response.json()['status'])

        submission = response.json()['result']

        time=[]
        rate = []
        maxRate=0
        for sub in submission:
            if(sub['verdict'] == 'OK'):
                problemRate = int(str(sub['problem'].get("rating", 0)))
                if(problemRate!=0):
                    time.append(sub['creationTimeSeconds'])
                    rate.append(problemRate)
                    maxRate = max(maxRate,problemRate)

        time.reverse()
        rate.reverse()

        fig, ax = plt.subplots()

        y_points = [0]
        i=0
        for y in range(800,3600,100):
            y_points.append(y)
            if(y_points[i]>maxRate):
                break
            i+=1

        ax.set_xticks([])
        ax.set_yticks(y_points[:i+1])

        color_area = [0,1200,1400,1600,1900,2100,2300,2400,2600,3000,4000]
        color = ['lightgray','limegreen','turquoise','royalblue','magenta','moccasin','orange','lightcoral','red','maroon']

        j=0
        for c in color:
            ax.axhspan(ymin=color_area[j], ymax=color_area[j+1], facecolor=c, alpha=0.6)
            j+=1
            if(color_area[j]>maxRate):
                break

        ax.scatter(time,rate,label = self.handle, marker='o' , color='gold')
        ax.legend()

        plt.savefig(fname='plotscatter')
        image = Image.open("plotscatter.png")
        return os.path.abspath(image.filename)
    
    def plot_problems(self):
        url = f'https://codeforces.com/api/user.status?handle={self.handle}'
        response = requests.get(url)
        print("Status -> " + response.json()['status'])

        problems = response.json()['result']
        problems.reverse()

        m = {}
        for problem in problems:
            try:
                problem_id = str(problem['problem']['contestId'])+str(problem['problem']['index'])
                if problem['verdict'] == 'OK' and problem_id in m and m[problem_id] == 'wrong':
                    m[problem_id] = "wrong+OK"
                elif problem['verdict'] == 'OK' :
                    m[problem_id] = 'OK'
                else:
                    m[problem_id] = 'wrong'
            except KeyError:
                pass

        count_ok = sum(1 for value in m.values() if value == 'OK')
        count_wrong_ok = sum(1 for value in m.values() if value == 'wrong+OK')
        count_wrong = sum(1 for value in m.values() if value == 'wrong')

        
        fig, ax = plt.subplots()
        x_values = ["Accepted from first time" , "Accepted after WA" , "Not solved yet"]
        y_values = [count_ok,count_wrong_ok,count_wrong]

        ax.bar(x_values,y_values,color=["limegreen","limegreen","lightgrey"],label=self.handle)
        ax.legend()

        plt.savefig(fname='plotproblems')
        image = Image.open("plotproblems.png")
        return os.path.abspath(image.filename)

    def Random_Problem(rating,handle):
        url = 'https://codeforces.com/api/problemset.problems'
        response = requests.get(url)
        print("Status -> " + response.json()['status'])

        problems = response.json()['result']['problems']
        if(rating<800 or rating>3500 or rating%100!=0):
            return "Invalid rating please choose a rate between (800 - 3500)"
        
        #####################

        url = f'https://codeforces.com/api/user.status?handle={handle}'
        response = requests.get(url)
        print("Status -> " + response.json()['status'])

        ALLsubmission = response.json()['result']
        submission = []
        for sub in ALLsubmission:
            if(sub['verdict']=='OK'):
                submission.append(sub)
        
        #####################
        selectedProblem = ''
        randomProblem = ""
        flag = True
        while True:
            i = random.randint(1, len(problems)-1000)
            while i<len(problems):
                flag = True
                if(rating == problems[i]['rating']):
                    for sub in submission:
                        try:
                            contest_id = sub['problem']['contestId']
                        except KeyError:
                            pass
                        if(contest_id == problems[i]['contestId'] and sub['problem']['index'] == problems[i]['index']):
                            flag = False
                    if flag:
                        selectedProblem = f"{problems[i]['contestId']}/{problems[i]['index']}"
                        randomProblem = (f"> ### [{problems[i]['index']}.{problems[i]['name']}](<https://codeforces.com/contest/{problems[i]['contestId']}/problem/{problems[i]['index']}>)\n> **Rate:** {problems[i]['rating']}\n")
                        break
                i+=1
            if flag:
                break
        file = open('Data.txt','r')
        data = file.readlines()
        i=0
        for line in data:
            user,file_handle,points,problem = line.split()
            if handle == file_handle:
                data[i] = f"{user} {file_handle} {points} {selectedProblem}\n"
            i+=1
        file = open('Data.txt','w')
        file.writelines(data)

        return randomProblem
                
    def Redeem_Points(handle):
        problemContestId,problemIndex = "",""
        user,file_handle,points,problem = "","",0,""
        file = open('Data.txt','r')
        data = file.readlines()
        i=0
        for line in data:
            user,file_handle,points,problem = line.split()
            points = int(points)
            if handle == file_handle:
                problemContestId,problemIndex = problem.split('/')

        url = f'https://codeforces.com/api/user.status?handle={handle}'
        response = requests.get(url)
        print("Status -> " + response.json()['status'])

        ALLsubmission = response.json()['result']
        m = {
            800:1,900:1,
            1000:2,1100:2,1200:2,
            1300:3,1400:3,
            1500:4,1600:4,
            1700:5,1800:5,
            1900:6,2000:6,
            2100:7,2200:7,
            2300:8,2400:8,
            2500:9,2600:9,
            2700:10,2800:10,
            2900:11,3000:11,
            3100:12,3200:12,
            3300:13,3400:13,3500:14
        }
        for sub in ALLsubmission:
            try:
                contest_id = sub['problem']['contestId']
            except KeyError:
                pass
            if(sub['verdict']=='OK' and str(problemContestId) == str(contest_id) and problemIndex == sub['problem']['index']):
                points+=m[int(sub['problem']['rating'])]
                data[i] = f"{user} {file_handle} {points} NULL\n"        
                file = open('Data.txt','w')
                file.writelines(data)                
                return f"You got {m[sub['problem']['rating']]} points"

        return f"> Solve the problem first to redeem points \n> https://codeforces.com/contest/{problemContestId}/problem/{problemIndex}"
    
    def leaderboard():
        file = open('Data.txt','r')
        data = file.readlines()
        message = f"> **Handle**                    **Points**\n> ---------------------------------------\n"
        for line in data:
            user,file_handle,points,problem = line.split()
            message+= f"> {file_handle}      {points}\n"
        return message