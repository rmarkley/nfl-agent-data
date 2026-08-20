import nfl_data_py as nfl
import pandas as pd

def get_defensive_tendencies(season):
    pbp = nfl.import_pbp_data([season])
    pbp = pbp[pbp['pass'] == 1]

    grouped = pbp.groupby('defteam').agg(
        plays=('play_id', 'count'),
        sacks=('sack', 'sum'),
        qb_hits=('qb_hit', 'sum'),
        avg_time_to_throw=('time_to_throw', 'mean') if 'time_to_throw' in pbp.columns else ('play_id', 'count')
    ).reset_index()

    grouped['sack_rate'] = (grouped['sacks'] / grouped['plays']).round(3)
    grouped['pressure_rate_proxy'] = ((grouped['sacks'] + grouped['qb_hits']) / grouped['plays']).round(3)

    return grouped.sort_values('pressure_rate_proxy', ascending=False)

def get_rush_defense(season):
    pbp = nfl.import_pbp_data([season])
    rush = pbp[pbp['rush'] == 1]

    grouped = rush.groupby('defteam').agg(
        rush_plays=('play_id', 'count'),
        avg_yards_allowed=('yards_gained', 'mean'),
        stuffed_rate=('yards_gained', lambda x: (x <= 0).mean())
    ).reset_index()

    return grouped.sort_values('avg_yards_allowed')

if __name__ == "__main__":
    season = 2025
    tendencies = get_defensive_tendencies(season)
    rush_def = get_rush_defense(season)
    tendencies.to_csv('data/raw/defensive_tendencies.csv', index=False)
    rush_def.to_csv('data/raw/rush_defense.csv', index=False)
    print("Saved pressure and rush defense data.")
