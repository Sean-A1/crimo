# core/urls_by_league.py
from django.urls import path, include
from common import views as common_views  # 이거 추가!

urlpatterns_by_league = [
    path(
        "<str:league>/",
        include(
            [
                path("", common_views.league_home, name="league_home"),  # ✅ 리그 루트
                path("match/", include("match.urls")),
                path("prediction/", include("prediction.urls")),
                path("leaderboards/", include("leaderboards.urls")),
                path("team/", include("team.urls")),
            ]
        ),
    ),
]
