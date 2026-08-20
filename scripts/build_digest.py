python
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

    # Pressure / pass rush tendencies
    try:
        pressure = pd.read_csv('data/raw/defensive_tendencies.csv')
        lines.append("## Pressure Tendencies (proxy for blitz aggression)\n")
        lines.append("| Team | Sack Rate | Pressure Rate |\n|---|---|---|")
        for _, row in pressure.iterrows():
            lines.append(f"| {row['defteam']} | {row['sack_rate']} | {row['pressure_rate_proxy']} |")
        lines.append("")
    except FileNotFoundError:
        pass

    # Rush defense
    try:
        rush = pd.read_csv('data/raw/rush_defense.csv')
        lines.append("## Run Defense (front-7 strength)\n")
        lines.append("| Team | Avg Yards Allowed | Stuffed Rate |\n|---|---|---|")
        for _, row in rush.iterrows():
            lines.append(f"| {row['defteam']} | {round(row['avg_yards_allowed'],2)} | {round(row['stuffed_rate'],2)} |")
        lines.append("")
    except FileNotFoundError:
        pass

    # Injuries
    injuries = load_json('data/raw/injuries.json', {})
    if injuries:
        lines.append("## Injuries\n")
        for team, players in injuries.items():
            if players:
                lines.append(f"**{team}**")
                for p in players if isinstance(players, list) else []:
                    lines.append(f"- {p}")
        lines.append("")

    # Adverse media
    adverse = load_json('data/raw/adverse_media.json', {})
    if adverse:
        lines.append("## Adverse Media Scan\n")
        for name, articles in adverse.items():
            lines.append(f"**{name}**")
            for a in articles[:5]:
                title = a.get('title', 'Untitled')
                url = a.get('url', '')
                lines.append(f"- {title} ({url})")
        lines.append("")

    with open('data/weekly_digest.md', 'w') as f:
        f.write("\n".join(lines))
    print("Digest built: data/weekly_digest.md")

if __name__ == "__main__":
    build()
