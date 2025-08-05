# team/views.py
from django.shortcuts import render, get_object_or_404
from .models import Team, Player


def team(request, league):
    request.session["league"] = league  # 세션 기반 분기 처리

    teams = (
        Team.objects.filter(league=league).exclude(team_id="고양").order_by("team_id")
    )

    # 현재 사용자가 선택한 리그 (kbo or mlb)에 해당하는 팀만 필터링

    # ✅ league도 템플릿에 전달
    return render(
        request,
        "team/index.html",
        {
            "team_list": teams,
            "league": league,
        },
    )


def player_list(request, league, team_id):
    request.session["league"] = league
    team = get_object_or_404(Team, id=team_id)
    players = Player.objects.filter(team=team)

    # ✅ player_list도 로고 분기를 위해 league 전달
    return render(
        request,
        "team/detail/index.html",
        {
            "team": team,
            "players": players,
            "league": team.league,
        },
    )
