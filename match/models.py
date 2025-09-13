from django.db import models


class Schedule(models.Model):
    league = models.CharField(
        max_length=10, choices=[("kbo", "KBO"), ("mlb", "MLB")], default="mlb"
    )

    year = models.IntegerField(default=2025)
    month = models.IntegerField()
    date = models.IntegerField()
    day = models.CharField(max_length=10)
    time = models.CharField(max_length=10)
    
    stadium = models.CharField(max_length=20)
    
    team1 = models.CharField(max_length=20)
    team2 = models.CharField(max_length=20)

    # 실제 경기 점수 추가
    score_team1 = models.IntegerField(null=True, blank=True)
    score_team2 = models.IntegerField(null=True, blank=True)

    # Admin selects main event
    is_main_event = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.month}/{self.date}({self.day}) {self.team1} vs {self.team2} - {self.stadium}"
