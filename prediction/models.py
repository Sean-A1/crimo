# prediction/models.py
from django.db import models
from datetime import datetime

TEAM_CODE_MAP = {
    # 파일의 match_id에 나오는 비표준 코드 보정
    "ATH": "OAK",  # Athletics
    "AZ": "ARI",   # D-backs
}

def normalize_code(code: str) -> str:
    if not code:
        return code
    return TEAM_CODE_MAP.get(code.upper(), code.upper())

class MlbPredClass(models.Model):
    # 날짜는 YYMMDD 문자열과 실제 DateField 둘 다 저장
    date_str = models.CharField(max_length=6, db_index=True)  # e.g. "250329"
    date = models.DateField(db_index=True)

    # 매치: "AWAY@HOME" 형태를 분해해서 저장
    away = models.CharField(max_length=4)       # 원본 코드 (예: ATH, AZ 등)
    home = models.CharField(max_length=4)
    
    away_norm = models.CharField(max_length=4, db_index=True)  # ✅ index
    home_norm = models.CharField(max_length=4, db_index=True)  # ✅ index

    # 예측값 (홈팀 승률이 proba_sigmoid)
    proba_sigmoid = models.FloatField()
    proba_isotonic = models.FloatField(null=True, blank=True)  # isotonic 없을 수도
    
    label = models.IntegerField(null=True, blank=True)         # ✅ 라벨 없어도 저장

    class Meta:
        unique_together = ("date_str", "away", "home")
        ordering = ["date", "away_norm", "home_norm"]  # ✅ 보기 좋게 정렬
        
    def __str__(self):
        return f"[{self.date_str}] {self.away_norm}@{self.home_norm} (p_sig={self.proba_sigmoid:.3f})"

    @property
    def home_pct(self) -> int:
        return round(self.proba_sigmoid * 100)

    @property
    def away_pct(self) -> int:
        return 100 - self.home_pct


class MlbPredReg(models.Model):
    # 공통 키
    date = models.DateField(db_index=True)
    date_str = models.CharField(max_length=6, db_index=True)  # YYMMDD (분류와 링크용)

    # 매치업 (HOME vs AWAY) + 표기 정규화
    home = models.CharField(max_length=4)       # 원본 코드
    away = models.CharField(max_length=4)
    
    home_norm = models.CharField(max_length=4, db_index=True)  # ✅ index
    away_norm = models.CharField(max_length=4, db_index=True)  # ✅ index

    # 예측 이닝 시나리오
    pred_inn_home = models.CharField(max_length=256)
    pred_inn_away = models.CharField(max_length=256)

    # 실제 이닝 시나리오
    act_inn_home = models.CharField(max_length=256, null=True, blank=True)
    act_inn_away = models.CharField(max_length=256, null=True, blank=True)

    # 합계
    pred_total_home = models.IntegerField(null=True, blank=True)
    pred_total_away = models.IntegerField(null=True, blank=True)
    act_total_home = models.IntegerField(null=True, blank=True)
    act_total_away = models.IntegerField(null=True, blank=True)
    
    # 상세 필드
    actual_starters    = models.CharField(max_length=200, null=True, blank=True)
    predicted_starters = models.CharField(max_length=200, null=True, blank=True)
    pitching_changes   = models.TextField(null=True, blank=True)
    game_pk            = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        unique_together = ("date_str", "away_norm", "home_norm")
        ordering = ["date", "away_norm", "home_norm"]  # ✅ 정렬

    def __str__(self):
        return f"[{self.date_str}] {self.away_norm} vs {self.home_norm}"
    
    def _split_nums(self, s: str):
        if not s:
            return []
        # ; 또는 | 둘 다 지원
        sep = ";" if ";" in s else ("|" if "|" in s else None)
        parts = s.split(sep) if sep else [s]
        vals = []
        for x in parts:
            x = x.strip()
            if x == "":
                continue
            try:
                vals.append(int(x))
            except Exception:
                # 숫자 변환 실패시 0으로 대체(안전)
                try:
                    vals.append(int(float(x)))
                except Exception:
                    vals.append(0)
        return vals

    def pred_lists(self):
        a = self._split_nums(self.pred_inn_away)
        h = self._split_nums(self.pred_inn_home)
        return a, h  # (away, home)

    @staticmethod
    def yymmdd(d):
        return f"{d.year%100:02d}{d.month:02d}{d.day:02d}"
    
    
class MlbClassMetric(models.Model):
    # 파일명 키
    date_str = models.CharField(max_length=6, db_index=True)  # e.g., 250329
    # 원본 코드(파일명에 쓰인 코드)
    away = models.CharField(max_length=8)
    home = models.CharField(max_length=8)
    # 정규화 코드(화면/URL 매칭용)
    away_norm = models.CharField(max_length=8, db_index=True)
    home_norm = models.CharField(max_length=8, db_index=True)

    # 내용(텍스트)
    valid_report = models.TextField(null=True, blank=True)
    test_report  = models.TextField(null=True, blank=True)

    # 이미지 파일 경로(절대/상대 상관없이 문자열로 저장)
    valid_confmat_path = models.CharField(max_length=512, null=True, blank=True)
    test_confmat_path  = models.CharField(max_length=512, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("date_str", "away", "home")
        ordering = ["date_str", "away_norm", "home_norm"]

    def __str__(self):
        return f"[{self.date_str}] {self.away}@{self.home}"