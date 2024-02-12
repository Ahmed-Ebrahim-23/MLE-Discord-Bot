import requests
from datetime import datetime, timedelta

class Contest:
    def __init__(self,id,name,duration,startTime,day):
        self.id = id
        self.name = name
        self.duration = duration
        self.startTime = startTime
        self.day = day

    def UpComing_Contests():
        url = 'https://codeforces.com/api/contest.list'
        response = requests.get(url)
        print("Status -> " + response.json()['status'])

        contests = response.json()['result']
        upcomingContests = []

        for contest in contests:
            if(contest["phase"]=="BEFORE"):
                # duration of the contest
                durationHours = str(int(contest["durationSeconds"]/(60*60)))
                durationMinute = str(int(contest["durationSeconds"]/60%60))
                if len(durationMinute)==1:
                    durationMinute = durationMinute*2
                duration = str(durationHours+":"+durationMinute)

                startTime = contest["startTimeSeconds"] 
                

                # Convert Unix timestamp to a datetime object
                unix_timestamp = contest["startTimeSeconds"] 
                normalFormat = datetime.utcfromtimestamp(unix_timestamp) + timedelta(hours=2)
                startTime = normalFormat.strftime('%d/%m/%Y %I:%M %p')
                
                day_of_week = normalFormat.weekday()
                day_name = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][day_of_week]

                con = Contest(contest["id"],contest["name"],duration,startTime,day_name)
                upcomingContests.append(con)
            else:
                break
        upcomingContests.reverse()
        response = ""
        for contest in upcomingContests:
            response = response + (f"### [{contest.name}](<https://codeforces.com/contests/{contest.id}>)\n**Contest Duration** {contest.duration}\n**Starts at** {contest.day}, {contest.startTime}")
            response = response + '\n\n'
        return response


                

        