from django.db import models


def team_logo_path(instance, filename):
    return f"team_logos/{instance.league}/{instance.team_id}.png"


class Team(models.Model):
    league = models.CharField(
        max_length=10, choices=[("kbo", "KBO"), ("mlb", "MLB")], default="mlb"
    )
    team_id = models.CharField(max_length=10, unique=True)  # 팀 ID (예: KIA)
    name = models.CharField(max_length=100)  # 팀 이름 (추후 추가 가능)
    logo = models.ImageField(upload_to=team_logo_path, null=True, blank=True)

    def __str__(self):
        return self.team_id


class Player(models.Model):
    backnumber = models.IntegerField(null=True, blank=True)  # 등번호
    player_id = models.CharField(max_length=50, unique=True)  # 선수 ID
    team = models.ForeignKey(Team, on_delete=models.CASCADE)  # 소속 팀 (ForeignKey)
    position = models.CharField(max_length=20)  # 포지션
    birthday = models.DateField()  # 생년월일
    profile = models.CharField(max_length=100)  # 신체 정보
    school = models.TextField()  # 학력

    ai_score = models.IntegerField(null=True, blank=True)
    stat = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.player_id} ({self.team.team_id})"
