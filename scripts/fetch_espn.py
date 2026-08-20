import requests
import json

TEAMS_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams"

def get_all_teams():
    r = requests.get(TEAMS_URL)
    r.raise_for_status()
    data = r.json()
    return [t['team']['abbreviation'] for t in data['sports'][0]['leagues'][0]['teams']]

def get_injuries(team_abbr):
    url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{team_abbr}/injuries"
    r = requests.get(url)
    if r.status_code != 200:
        return []
    return r.json()

if __name__ == "__main__":
    teams = get_all_teams()
    all_injuries = {}
    for t in teams:
        all_injuries[t] = get_injuries(t)
    with open('data/raw/injuries.json', 'w') as f:
        json.dump(all_injuries, f, indent=2)
    print(f"Saved injury data for {len(teams)} teams.")
