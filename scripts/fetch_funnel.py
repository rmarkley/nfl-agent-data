import nfl_data_py as nfl
import pandas as pd

def build_funnel_flags(season):
    pbp = nfl.import_pbp_data([season])
    pbp = pbp[pbp['play_type'].isin(['pass', 'run'])]

    rush = pbp[pbp['play_type'] == 'run']
    passp = pbp[pbp['play_type'] == 'pass']

    rush_def = rush.groupby('defteam')['epa'].mean().rename('rush_epa_allowed')
    pass_def = passp.groupby('defteam')['epa'].mean().rename('pass_epa_allowed')

    combined = pd.concat([rush_def, pass_def], axis=1).reset_index().rename(columns={'defteam': 'team'})

    combined['rush_def_rank'] = combined['rush_epa_allowed'].rank()
    combined['pass_def_rank'] = combined['pass_epa_allowed'].rank()

    def classify(row):
        if row['rush_def_rank'] <= 16 and row['pass_def_rank'] > 16:
            return 'Pass Funnel (stops run, vulnerable to pass)'
        elif row['pass_def_rank'] <= 16 and row['rush_def_rank'] > 16:
            return 'Run Funnel (stops pass, vulnerable to run)'
        elif row['rush_def_rank'] <= 16 and row['pass_def_rank'] <= 16:
            return 'Balanced/Strong (tough matchup both ways)'
        else:
            return 'Balanced/Weak (exploitable both ways)'

    combined['funnel_flag'] = combined.apply(classify, axis=1)
    return combined.sort_values('funnel_flag')

if __name__ == "__main__":
    season = 2025
    funnel = build_funnel_flags(season)
    funnel.to_csv('data/raw/funnel_flags.csv', index=False)
    print("Funnel flags saved.")
