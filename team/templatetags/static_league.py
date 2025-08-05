from django import template
from django.templatetags.static import static

register = template.Library()


@register.simple_tag
def static_team_logo(team_name, league):
    """팀 로고 경로 반환"""
    return static(f"images/teams/{league}/{team_name}.png")


@register.simple_tag
def static_prediction_image(date_str, team1, team2, league):
    """예측 이미지 경로 반환"""
    return static(f"images/prediction/{league}/{date_str}_{team1}_{team2}.png")


@register.simple_tag
def static_player_image(player_id, league):
    """선수 이미지 경로 반환"""
    return static(f"images/players/{league}/{player_id}.png")
