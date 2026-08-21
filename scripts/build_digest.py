import pandas as pd
import json
from datetime import datetime

def load_json(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return default or {}

def build():
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"# NFL Weekly Digest — updated {ts}\n"]

    def add_table(path, title, sort_by=None, ascending=False, top_n=32):
        try:
            df = pd.read_csv(path)
            if sort_by and sort_by in df.columns:
                df = df.sort_values(sort_by, ascending=ascending)
            df = df.head(top_n)
            lines.append(f"## {title}\n")
            lines.append("| " + " | ".join(df.columns) + " |")
            lines.append("|" + "---|" * len(df.columns))
            for _, row in df.iterrows():
                lines.append("| " + " | ".join(str(v) for v in row.values) + " |")
            lines.append("")
        except FileNotFoundError:
            pass

    # --- Core pressure / rush defense (from fetch_pbp.py) ---
    add_table('data/raw/defensive_tendencies.csv', 'Pressure Tendencies (proxy for blitz aggression)', sort_by='pressure_rate_proxy')
    add_table('data/raw/rush_defense.csv', 'Run Defense (front-7 strength)', sort_by='avg_yards_allowed', ascending=True)

    # --- Tactics / matchups (from fetch_tactics.py) ---
    add_table('data/raw/epa_offense.csv', 'Offensive EPA/Success Rate by Situation', sort_by='epa_per_play')
    add_table('data/raw/epa_defense.csv', 'Defensive EPA/Success Rate Allowed by Situation', sort_by='epa_allowed', ascending=True)
    add_table('data/raw/play_action.csv', 'Play-Action Tendency by Team', sort_by='pa_rate')
    add_table('data/raw/fourth_down.csv', '4th Down Aggressiveness by Team', sort_by='go_rate')
    add_table('data/raw/redzone_offense.csv', 'Red Zone TD% (Offense)', sort_by='rz_td_rate')
    add_table('data/raw/redzone_defense.csv', 'Red Zone TD% Allowed (Defense)', sort_by='rz_td_rate_allowed', ascending=True)
    add_table('data/raw/target_share.csv', 'Target Share & Depth of Target by Player', sort_by='target_share', top_n=64)
    add_table('data/raw/snap_counts.csv', 'Snap Count Trends', top_n=64)
    add_table('data/raw/rest_travel.csv', 'Rest Days by Matchup', top_n=32)

    # --- Fantasy matchup grid (from fetch_fantasy_matchups.py) ---
add_table('data/raw/fantasy_matchup_full_season.csv', 'Fantasy: Matchup Ratings — Full Season (All 17 Weeks)', sort_by='week', ascending=True, top_n=600)    # --- Full season schedule grid (from fetch_schedule_grid.py) ---
    add_table('data/raw/schedule_grid.csv', 'Full Season Schedule Grid (32 Teams x 18 Weeks)', top_n=32)

    # --- Funnel flags (from fetch_funnel.py) ---
    add_table('data/raw/funnel_flags.csv', 'Defensive Funnel Flags', sort_by='funnel_flag', top_n=32)

    # --- Injuries (from fetch_espn.py) ---
    injuries = load_json('data/raw/injuries.json', {})
    if injuries:
        lines.append("## Injuries\n")
        any_data = False
        for team, players in injuries.items():
            if players:
                any_data = True
                lines.append(f"**{team}**")
                for p in players if isinstance(players, list) else []:
                    if isinstance(p, dict):
                        name = p.get('athlete', {}).get('displayName', 'Unknown') if isinstance(p.get('athlete'), dict) else p.get('name', 'Unknown')
                        status = p.get('status', p.get('type', {}).get('description', 'Unknown status') if isinstance(p.get('type'), dict) else 'Unknown status')
                        lines.append(f"- {name}: {status}")
                    else:
                        lines.append(f"- {p}")
        if not any_data:
            lines.append("*No injury data currently reported (typical during preseason — check back closer to Week 1).*")
        lines.append("")

    # --- Adverse media (from fetch_news.py) ---
    adverse = load_json('data/raw/adverse_media.json', {})
    if adverse:
        lines.append("## Adverse Media Scan\n")
        for name, articles in adverse.items():
            if articles:
                lines.append(f"**{name}**")
                for a in articles[:5]:
                    title = a.get('title', 'Untitled')
                    url = a.get('url', '')
                    lines.append(f"- {title} ({url})")
        lines.append("")

    with open('weekly_digest.md', 'w') as f:
        f.write("\n".join(lines))
    print("Digest built: weekly_digest.md")

if __name__ == "__main__":
    build()
