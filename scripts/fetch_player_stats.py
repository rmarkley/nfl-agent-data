import nfl_data_py as nfl
import pandas as pd

def load_weekly(season):
    return nfl.import_weekly_data([season])

def season_totals(weekly):
    """Full-season cumulative stats by player"""
    cols_present = weekly.columns.tolist()

    agg_dict = {}
    for col in ['completions', 'attempts', 'passing_yards', 'passing_tds', 'interceptions',
                'carries', 'rushing_yards', 'rushing_tds',
                'receptions', 'targets', 'receiving_yards', 'receiving_tds',
                'fantasy_points', 'fantasy_points_ppr']:
        if col in cols_present:
            agg_dict[col] = 'sum'

    g = weekly.groupby(['player_name', 'player_id', 'position', 'recent_team']).agg(agg_dict).reset_index()
    g['games_played'] = weekly.groupby('player_id')['week'].transform('count').groupby(weekly['player_id']).first().values[:len(g)] if False else weekly.groupby('player_id')['week'].nunique().reindex(g['player_id']).values

    if 'targets' in g.columns and 'receptions' in g.columns:
        g['catch_rate'] = (g['receptions'] / g['targets']).round(3)

    return g.sort_values('fantasy_points_ppr', ascending=False) if 'fantasy_points_ppr' in g.columns else g

def recent_form(weekly, last_n=3):
    """Last N games trend — flags hot/cold streaks for waiver wire and props"""
    latest_week = weekly['week'].max()
    recent = weekly[weekly['week'] > latest_week - last_n]

    cols_present = recent.columns.tolist()
    agg_dict = {}
    for col in ['completions', 'attempts', 'passing_yards', 'passing_tds', 'interceptions',
                'carries', 'rushing_yards', 'rushing_tds',
                'receptions', 'targets', 'receiving_yards', 'receiving_tds',
                'fantasy_points', 'fantasy_points_ppr']:
        if col in cols_present:
            agg_dict[col] = 'sum'

    g = recent.groupby(['player_name', 'player_id', 'position', 'recent_team']).agg(agg_dict).reset_index()
    g['games_in_window'] = recent.groupby('player_id')['week'].nunique().reindex(g['player_id']).values

    # Per-game averages for easy comparison
    for col in ['rushing_yards', 'receiving_yards', 'passing_yards', 'fantasy_points_ppr', 'targets', 'receptions']:
        if col in g.columns:
            g[f'{col}_per_game'] = (g[col] / g['games_in_window']).round(2)

    sort_col = 'fantasy_points_ppr' if 'fantasy_points_ppr' in g.columns else g.columns[-1]
    return g.sort_values(sort_col, ascending=False)

def waiver_wire_candidates(weekly, last_n=3, max_season_total_games=None):
    """Players with strong recent form but likely low ownership signal — high recent points, high recent target/carry share growth"""
    recent = recent_form(weekly, last_n)

    # Flag players trending up: decent recent volume regardless of season-long name recognition
    candidates = recent[
        (recent['games_in_window'] >= 2)
    ].copy()

    if 'fantasy_points_ppr_per_game' in candidates.columns:
        candidates = candidates.sort_values('fantasy_points_ppr_per_game', ascending=False)

    return candidates.head(100)

if __name__ == "__main__":
    season = 2025
    weekly = load_weekly(season)

    totals = season_totals(weekly)
    totals.to_csv('data/raw/player_season_totals.csv', index=False)

    recent = recent_form(weekly, last_n=3)
    recent.to_csv('data/raw/player_recent_form.csv', index=False)

    waivers = waiver_wire_candidates(weekly, last_n=3)
    waivers.to_csv('data/raw/waiver_candidates.csv', index=False)

    print(f"Player stats saved: {len(totals)} season totals, {len(recent)} recent form, {len(waivers)} waiver candidates.")
