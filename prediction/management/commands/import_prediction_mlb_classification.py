# prediction/management/commands/import_prediction_mlb_classification.py
import os
import re
from datetime import date
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from openpyxl import load_workbook

from prediction.models import MlbPredClass, normalize_code

class Command(BaseCommand):
    help = "MLB 분류 예측 결과(xlsx)를 임포트합니다 (baseball_data/2025/web_data/_YYYYMMDD-YYYYMMDD_pred.xlsx)."

    FILE_PATTERN = re.compile(r"^_([0-9]{6})-([0-9]{6})_pred\.xlsx$")
    SHEET_NAME = "predictions"  # 시트명

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            help="파일 경로를 직접 지정 (미지정 시 최신 패턴 파일 자동 선택)",
        )

    def handle(self, *args, **options):
        base_dir = Path(settings.BASE_DIR) / "baseball_data" / "2025" / "web_data"
        if not base_dir.exists():
            self.stderr.write(f"❌ 경로 없음: {base_dir}")
            return

        # 파일 선택
        file_path = options.get("path")
        if file_path:
            xlsx = Path(file_path)
            if not xlsx.exists():
                self.stderr.write(f"❌ 파일 없음: {xlsx}")
                return
        else:
            # 패턴 매칭되는 파일 중 수정시간 최신 1개
            candidates = [
                p for p in base_dir.iterdir()
                if p.is_file() and self.FILE_PATTERN.match(p.name)
            ]
            if not candidates:
                self.stderr.write("❌ 패턴에 맞는 파일이 없습니다: _YYYYMMDD-YYYYMMDD_pred.xlsx")
                return
            xlsx = max(candidates, key=lambda p: p.stat().st_mtime)

        self.stdout.write(f"📥 임포트 파일: {xlsx.name}")

        wb = load_workbook(xlsx, read_only=True, data_only=True)
        
        if self.SHEET_NAME not in wb.sheetnames:
            self.stderr.write(f"❌ 시트 '{self.SHEET_NAME}' 를 찾을 수 없습니다. 시트들: {wb.sheetnames}")
            return
        
        ws = wb[self.SHEET_NAME]

        # 헤더 행 찾기
        header = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
        name_to_idx = {name: idx for idx, name in enumerate(header)}

        required = ["date_str", "match_id", "proba_sigmoid", "proba_isotonic", "label"]
        for r in required:
            if r not in name_to_idx:
                self.stderr.write(f"❌ 헤더에 '{r}' 컬럼이 없습니다.")
                return

        # 파일 내 중복(같은 date_str+match)일 때 마지막 줄을 채택
        latest = {}
        seen_dates = set()
        rows_read = rows_kept = 0

        for r in ws.iter_rows(min_row=2):
            rows_read += 1
            date_str_cell = r[name_to_idx["date_str"]].value
            match_id_cell = r[name_to_idx["match_id"]].value
            ps_cell = r[name_to_idx["proba_sigmoid"]].value
            pi_cell = r[name_to_idx["proba_isotonic"]].value
            label_cell = r[name_to_idx["label"]].value

            if not date_str_cell or not match_id_cell:
                continue

            date_str = str(date_str_cell).strip()
            match_id = str(match_id_cell).strip()

            if "@" not in match_id:
                continue
            away, home = [x.strip().upper() for x in match_id.split("@", 1)]

            # "250329" -> 2025-03-29
            try:
                yy = int(date_str[:2]); mm = int(date_str[2:4]); dd = int(date_str[4:6])
                dt = date(2000 + yy, mm, dd)
            except Exception:
                continue

            try:
                ps = float(ps_cell)
                pi = float(pi_cell)
                label = int(label_cell)
            except Exception:
                continue

            key = (date_str, away, home)
            latest[key] = {
                "date_str": date_str,
                "date": dt,
                "away": away,
                "home": home,
                "away_norm": normalize_code(away),
                "home_norm": normalize_code(home),
                "proba_sigmoid": ps,
                "proba_isotonic": pi,
                "label": label,
            }
            seen_dates.add(date_str)
            rows_kept += 1

        # 같은 날짜들 선삭제 후 저장
        if seen_dates:
            MlbPredClass.objects.filter(date_str__in=seen_dates).delete()

        objs = [MlbPredClass(**v) for v in latest.values()]
        MlbPredClass.objects.bulk_create(objs, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(
            f"✅ 읽은 행 {rows_read} → 저장 {len(objs)}건 (날짜 {len(seen_dates)}개)"
        ))
