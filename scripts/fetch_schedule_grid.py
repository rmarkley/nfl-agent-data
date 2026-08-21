import nfl_data_py as nfl
import pandas as pd

def build_schedule_grid(season):
    sched = nfl.import_schedules([season])
    sched = sched[['week', 'home_team', 'away_team']].dropna()

    teams = sorted(set(sched['home_team']) | set(sched['away_team']))
    weeks = range(1, 19)

    grid = pd.DataFrame(index=teams, columns=[f"Week_{w}" for w in weeks])

    for _, g in sched.iterrows():
        week_col = f"Week_{int(g['week'])}"
        grid.loc[g['home_team'], week_col] = f"vs {g['away_team']}"
        grid.loc[g['away_team'], week_col] = f"@ {g['home_team']}"

    grid = grid.fillna("BYE")
    grid.index.name = "team"
    return grid.reset_index()

if __name__ == "__main__":
    season = 2025
    grid = build_schedule_grid(season)
    grid.to_csv('data/raw/schedule_grid.csv', index=False)
    print(f"Schedule grid saved: {grid.shape[0]} teams x {grid.shape[1]-1} weeks")
