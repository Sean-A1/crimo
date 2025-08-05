# team/templatetags/team_color.py

from django import template

register = template.Library()

TEAM_COLORS = {
    # ✅ KBO
    "KIA": "#e61e2b",
    "LG": "#242265",
    "삼성": "#0073cf",
    "두산": "#13294b",
    "한화": "#ff8200",
    "키움": "#6e0b14",
    "롯데": "#c8102e",
    "SSG": "#c60c30",
    "NC": "#003366",
    "KT": "#231f20",
    # ✅ MLB (예시 추가)
    "ARI": "#A71930",  # Arizona Diamondbacks
    "ATL": "#7C0A02",  # Atlanta Braves (버건디 계열, 대비 강조)
    "BAL": "#CC5500",  # Baltimore Orioles (딥 오렌지)
    "BOS": "#BD3039",  # Boston Red Sox
    "CHC": "#0E3386",  # Chicago Cubs
    "CHW": "#1C1C1C",  # Chicago White Sox (블랙)
    "CIN": "#8B0000",  # Cincinnati Reds (다크 레드)
    "CLE": "#002147",  # Cleveland Guardians (딥 네이비)
    "COL": "#33006F",  # Colorado Rockies
    "DET": "#1A1A1A",  # Detroit Tigers (딥 그레이)
    "HOU": "#002D62",  # Houston Astros
    "KC": "#00338D",  # Kansas City Royals (딥 블루)
    "LAA": "#BA0021",  # Los Angeles Angels
    "LAD": "#003B75",  # Los Angeles Dodgers (로열 네이비)
    "MIA": "#00A3E0",  # Miami Marlins
    "MIL": "#12284B",  # Milwaukee Brewers
    "MIN": "#021B40",  # Minnesota Twins (네이비 강화)
    "NYM": "#002D72",  # New York Mets
    "NYY": "#0D1117",  # New York Yankees (딥 블랙그레이)
    "OAK": "#004225",  # Oakland Athletics (다크 그린)
    "PHI": "#E81828",  # Philadelphia Phillies
    "PIT": "#27251F",  # Pittsburgh Pirates (블랙)
    "SD": "#4E3629",  # San Diego Padres (다크 브라운)
    "SEA": "#0C2C56",  # Seattle Mariners
    "SF": "#C1440E",  # San Francisco Giants (딥 오렌지)
    "STL": "#8B1C2D",  # St. Louis Cardinals (다크 레드)
    "TB": "#002244",  # Tampa Bay Rays (다크 네이비)
    "TEX": "#003278",  # Texas Rangers
    "TOR": "#134A8E",  # Toronto Blue Jays
    "WSH": "#800020",  # Washington Nationals (버건디)
}


@register.simple_tag
def team_color(team_id):
    return TEAM_COLORS.get(team_id, "#666666")  # fallback color
