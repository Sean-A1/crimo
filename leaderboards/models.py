# leaderboards/models.py
from django.db import models
from prediction.models import normalize_code  # ATH→OAK, AZ→ARI 등 재사용

class PlayerStatMLB(models.Model):
    season = models.IntegerField(db_index=True, default=2025)
    league = models.CharField(max_length=8, db_index=True, default="mlb")

    # 기본
    rank = models.IntegerField(db_index=True)
    player = models.CharField(max_length=100)
    age = models.IntegerField(null=True, blank=True)

    team = models.CharField(max_length=8, db_index=True)       # 원본(ATH 등)
    team_norm = models.CharField(max_length=8, db_index=True)  # 정규화(OAK 등)
    lg = models.CharField(max_length=8, db_index=True)         # AL/NL

    # 누계/율 스탯
    WAR = models.FloatField(null=True, blank=True)
    G   = models.IntegerField(null=True, blank=True)
    PA  = models.IntegerField(null=True, blank=True)
    AB  = models.IntegerField(null=True, blank=True)
    R   = models.IntegerField(null=True, blank=True)
    H   = models.IntegerField(null=True, blank=True)
    _2B = models.IntegerField(null=True, blank=True)
    _3B = models.IntegerField(null=True, blank=True)
    HR  = models.IntegerField(null=True, blank=True)
    RBI = models.IntegerField(null=True, blank=True)
    SB  = models.IntegerField(null=True, blank=True)
    CS  = models.IntegerField(null=True, blank=True)
    BB  = models.IntegerField(null=True, blank=True)
    SO  = models.IntegerField(null=True, blank=True)

    BA  = models.FloatField(null=True, blank=True)
    OBP = models.FloatField(null=True, blank=True)
    SLG = models.FloatField(null=True, blank=True)
    OPS = models.FloatField(null=True, blank=True)
    OPS_plus = models.IntegerField(null=True, blank=True)  # OPS+

    rOBA = models.FloatField(null=True, blank=True)
    Rbat_plus = models.IntegerField(null=True, blank=True)  # Rbat+
    TB  = models.IntegerField(null=True, blank=True)
    GIDP = models.IntegerField(null=True, blank=True)
    HBP = models.IntegerField(null=True, blank=True)
    SH  = models.IntegerField(null=True, blank=True)
    SF  = models.IntegerField(null=True, blank=True)
    IBB = models.IntegerField(null=True, blank=True)

    Pos = models.CharField(max_length=50, null=True, blank=True)
    Awards = models.CharField(max_length=100, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("season", "league", "player", "team_norm")
        ordering = ["-WAR", "rank"]

    def __str__(self):
        return f"[{self.season}] {self.player} ({self.team_norm}) WAR={self.WAR}"
