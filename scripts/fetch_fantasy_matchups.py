import nfl_data_py as nfl
import pandas as pd

def load_pbp(season):
    return nfl.import_pbp_data([season])

def defense_strength_by_position(pbp):
    pbp = pbp[pbp['play_type'].isin(['pass', 'run'])].copy()

    rush = pbp[pbp['play_type'] == 'run']
    rush_def = rush.groupby('defteam').agg(
        rush_epa_allowed=('epa', 'mean'),
        rush_success_allowed=('success', 'mean'),
        ypc_allowed=('yards_gained', 'mean')
    ).reset_index()
    rush_def['rush_matchup_rank'] = rush_def['rush_epa_allowed'].rank(ascending=False)

    pass_plays = pbp[pbp['play_type'] == 'pass'].dropna(subset=['receiver_player_name'])
    pass_def = pass_plays.groupby('defteam').agg(
        pass_epa_allowed=('epa', 'mean'),
        pass_success_allowed=('success', 'mean'),
        yards_allowed=('yards_gained', 'mean')
    ).reset_index()
    pass_def['pass_matchup_rank'] = pass_def['pass_epa_allowed'].rank(ascending=False)

    return rush_def, pass_def

def build_schedule_matchup_grid(season, rush_def, pass_def):
    sched = nfl.import_schedules([season])
    sched = sched[['week', 'home_team', 'away_team', 'gameday']].dropna()

    rows = []
    for _, g in sched.iterrows():
        for team, opp in [(g['home_team'], g['away_team']), (g['away_team'], g['home_team'])]:
            rush_row = rush_def[rush_def['defteam'] == opp]
            pass_row = pass_def[pass_def['defteam'] == opp]

            rows.append({
                'week': g['week'],
                'team': team,
                'opponent': opp,
                'gameday': g['gameday'],
                'opp_rush_epa_allowed': rush_row['rush_epa_allowed'].values[0] if len(rush_row) else None,
                'opp_rush_matchup_rank': rush_row['rush_matchup_rank'].values[0] if len(rush_row) else None,
                'opp_pass_epa_allowed': pass_row['pass_epa_allowed'].values[0] if len(pass_row) else None,
                'opp_pass_matchup_rank': pass_row['pass_matchup_rank'].values[0] if len(pass_row) else None,
            })

    grid = pd.DataFrame(rows)
    grid['rb_matchup_grade'] = grid['opp_rush_matchup_rank'].apply(
        lambda r: 'Elite (smash)' if r <= 8 else ('Good' if r <= 16 else ('Tough' if r <= 24 else 'Avoid'))
    )
    grid['pass_matchup_grade'] = grid['opp_pass_matchup_rank'].apply(
        lambda r: 'Elite (smash)' if r <= 8 else ('Good' if r <= 16 else ('Tough' if r <= 24 else 'Avoid'))
    )
    return grid

if __name__ == "__main__":
    season = 2025
    pbp = load_pbp(season)
    rush_def, pass_def = defense_strength_by_position(pbp)

    grid = build_schedule_matchup_grid(season, rush_def, pass_def)
    grid.to_csv('data/raw/fantasy_matchup_full_season.csv', index=False)

    print("Fantasy matchup grid saved.")
