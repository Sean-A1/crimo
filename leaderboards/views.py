from django.shortcuts import render
from team.models import Player


def leaderboard_view(request, league):
    request.session["league"] = league

    players = Player.objects.filter(
        team__league=league, ai_score__isnull=False
    ).order_by("-ai_score")

    context = {
        "players": players,
        "league": league,
    }
    return render(request, "leaderboards/index.html", context)
