# leaderboards/views.py
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from leaderboards.models import PlayerStatMLB

ALLOWED_ORDER = {
    "WAR": "-WAR",
    "OPS+": "-OPS_plus",
    "OPS": "-OPS",
    "HR": "-HR",
    "RBI": "-RBI",
    "SB": "-SB",
    "BA": "-BA",
    "OBP": "-OBP",
    "SLG": "-SLG",
    "TB": "-TB",
    "SO": "SO",   # 삼진 적은 순은 +SO로 바꾸고 싶으면 수정
    "BB": "-BB",
    "R": "-R",
    "H": "-H",
    "PA": "-PA",
    "Rank": "rank",
}

ORDER_OPTIONS = ["WAR","OPS+","OPS","HR","RBI","SB","BA","OBP","SLG","TB","SO","BB","R","H","PA","Rank"]

def leaderboard(request, league):
    season = int(request.GET.get("season") or 2025)
    q      = (request.GET.get("q") or "").strip()
    team   = (request.GET.get("team") or "").strip().upper()
    order_key = request.GET.get("order") or "WAR"

    qs = PlayerStatMLB.objects.filter(league=league.lower(), season=season)
    
    if q:
        qs = qs.filter(Q(player__icontains=q))
    if team:
        qs = qs.filter(team_norm=team)
        
    # 정렬
    field = ALLOWED_ORDER.get(order_key, "-WAR")
    qs = qs.order_by(field)

    # 팀 목록
    teams = list(
        PlayerStatMLB.objects.filter(league=league.lower(), season=season)
        .values_list("team_norm", flat=True).distinct()
    )
    teams.sort()

    paginator = Paginator(qs, 50)
    page_obj = paginator.get_page(request.GET.get("page"))


    ctx = {
        "league": league,
        "season": season,
        "q": q,
        "team": team,
        "order": order_key,
        "teams": teams,
        "page_obj": page_obj,
        "order_options": ORDER_OPTIONS,   # ✅ 추가
    }
    return render(request, "leaderboards/leaderboard.html", ctx)
