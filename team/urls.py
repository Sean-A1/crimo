from django.urls import path
from . import views

app_name = 'team'

urlpatterns = [
    path('', views.team, name='team_list'),  # 메인 페이지에서 팀 목록 표시
    path('players/', views.player_list, name='player_list'),
    path('players/<int:team_id>/', views.player_list, name='player_list'),


]
