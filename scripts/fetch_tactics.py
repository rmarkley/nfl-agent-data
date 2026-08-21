import nfl_data_py as nfl
import pandas as pd

def load_pbp(season):
    return nfl.import_pbp_data([season])

def epa_success_splits(pbp):
    pbp = pbp[pbp['play_type'].isin(['pass', 'run'])]

    def summarize(df, label):
        g = df.groupby('posteam').agg(
            plays=('play_id', 'count'),
            epa_per_play=('epa', 'mean'),
            success_rate=('success', 'mean')
        ).reset_index()
        g['split'] = label
        return g

    early = pbp[pbp['down'].isin([1, 2])]
    late = pbp[pbp['down'].isin([3, 4])]
    redzone = pbp[pbp['yardline_100'] <= 20]

    off = pd.concat([
        summarize(early, 'early_down'),
        summarize(late, 'late_down'),
        summarize(redzone, 'red_zone')
    ])

    def summarize_def(df, label):
        g = df.groupby('defteam').agg(
            plays=('play_id', 'count'),
            epa_allowed=('epa', 'mean'),
            success_rate_allowed=('success', 'mean')
        ).reset_index()
        g['split'] = label
        return g

    defn = pd.concat([
        summarize_def(early, 'early_down'),
        summarize_def(late, 'late_down'),
        summarize_def(redzone, 'red_zone')
    ])

    return off, defn

def play_action_tendencies(pbp):
    pass_plays = pbp[pbp['play_type'] == 'pass']
    g = pass_plays.groupby('posteam').agg(
        pass_plays=('play_id', 'count'),
        pa_rate=('play_action', 'mean')
    ).reset_index()
    return g.sort_values('pa_rate', ascending=False)

def fourth_down_aggressiveness(pbp):
    fourth = pbp[pbp['down'] == 4]
    g = fourth.groupby('posteam').agg(
        fourth_downs=('play_id', 'count'),
        go_rate=('play_type', lambda x: (x.isin(['pass', 'run'])).mean())
    ).reset_index()
    return g.sort_values('go_rate', ascending=False)

def redzone_efficiency(pbp):
    rz = pbp[(pbp['yardline_100'] <= 20) & (pbp['play_type'].isin(['pass', 'run']))]

    off = rz.groupby('posteam').agg(
        rz_plays=('play_id', 'count'),
        rz_td_rate=('touchdown', 'mean')
    ).reset_index()

    defn = rz.groupby('defteam').agg(
        rz_plays_faced=('play_id', 'count'),
        rz_td_rate_allowed=('touchdown', 'mean')
    ).reset_index()

    return off, defn

def target_share_and_adot(pbp):
    targets = pbp[pbp['play_type'] == 'pass'].dropna(subset=['receiver_player_name'])
    team_targets = targets.groupby('posteam')['play_id'].count().rename('team_total_targets')

    g = targets.groupby(['posteam', 'receiver_player_name']).agg(
        targets=('play_id', 'count'),
        avg_depth_of_target=('air_yards', 'mean'),
        yards_per_target=('yards_gained', 'mean')
    ).reset_index()

    g = g.merge(team_targets, on='posteam')
    g['target_share'] = (g['targets'] / g['team_total_targets']).round(3)
    return g[g['targets'] >= 5].sort_values('target_share', ascending=False)

def snap_count_trends(season):
    try:
        snaps = nfl.import_snap_counts([season])
        return snaps
    except Exception as e:
        print(f"Snap count pull failed: {e}")
        return pd.DataFrame()

def rest_and_travel(season):
    sched = nfl.import_schedules([season])
    cols = ['week', 'away_team', 'home_team', 'gameday', 'away_rest', 'home_rest']
    return sched[[c for c in cols if c in sched.columns]]

if __name__ == "__main__":
    season = 2025
    pbp = load_pbp(season)

    epa_off, epa_def = epa_success_splits(pbp)
    epa_off.to_csv('data/raw/epa_offense.csv', index=False)
    epa_def.to_csv('data/raw/epa_defense.csv', index=False)

    play_action_tendencies(pbp).to_csv('data/raw/play_action.csv', index=False)
    fourth_down_aggressiveness(pbp).to_csv('data/raw/fourth_down.csv', index=False)

    rz_off, rz_def = redzone_efficiency(pbp)
    rz_off.to_csv('data/raw/redzone_offense.csv', index=False)
    rz_def.to_csv('data/raw/redzone_defense.csv', index=False)

    target_share_and_adot(pbp).to_csv('data/raw/target_share.csv', index=False)
    snap_count_trends(season).to_csv('data/raw/snap_counts.csv', index=False)
    rest_and_travel(season).to_csv('data/raw/rest_travel.csv', index=False)

    print("All tactics/matchup tables saved.")
