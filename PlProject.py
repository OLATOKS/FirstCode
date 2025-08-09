import os
import requests
from dotenv import load_dotenv

load_dotenv() #loads the .env file

ApiKey = os.getenv("API_FOOTBALL_KEY")
LeagueId = 39
season = 2023

Url =  f"https://v3.football.api-sports.io/standings?league={LeagueId}&season={season}"

headers={"x-apisports-key":ApiKey}
Response = requests.get(Url, headers=headers)
data = Response.json()

Standings = data['response'][0]['league']['standings'][0]
for position in Standings:
    #print(position)
    Rank = position['rank']
    Team = position['team']['name']
    Points = position['points']
    Wins = position['all']['win']
    Losses = position['all']['lose']
    Draw = position['all']['draw']
    GoalDiff = position['goalsDiff']
    Goals1 = position['all']['goals']['for']
    Goals2 = position['all']['goals']['against']
    Played = position["all"]["played"]
    print(
        f"position {Rank} - {Team} - {Points} Pts - played {Played} - wins {Wins} - Losses {Losses} - Draws {Draw} - Goal difference {GoalDiff} - Goals for {Goals1} - Goals against {Goals2}"
        )

