from django.contrib import admin
from django.urls import path, include
from pybo.views import base_views
from common import views as common_views
from config import urls_by_league

from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),
    # path('', common_views.home, name='home'),  # 루트 URL → 홈화면
    path("", common_views.home1, name="home1"),
    
    # favicon.ico 무시 또는 대체 경로
    path("favicon.ico", RedirectView.as_view(url="/static/images/favicon.ico")),
    path("<str:league>/", common_views.league_home, name="league_home"),  # 리그 전용 홈
    
    # 리그별 앱 네임스페이스 등록 (중복 없이 한 번만!)
    path("<str:league>/prediction/",  include(("prediction.urls",  "prediction"),  namespace="prediction")),
    path("<str:league>/leaderboards/", include(("leaderboards.urls","leaderboards"), namespace="leaderboards")),
    path("<str:league>/team/",         include(("team.urls",        "team"),        namespace="team")),
    path("<str:league>/match/",        include(("match.urls",       "match"),       namespace="match")),

    
    path("common/", include("common.urls")),  # 로그인/회원가입 등
    
    
    path("pybo/", include("pybo.urls")),
    #
    # 리그 기반 URL 구조
    # path("", include(urls_by_league.urlpatterns_by_league)),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
