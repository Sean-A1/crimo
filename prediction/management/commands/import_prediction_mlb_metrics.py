# prediction/management/commands/import_prediction_mlb_metrics.py
import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from prediction.models import MlbClassMetric, normalize_code


class Command(BaseCommand):
    help = "MLB 분류 성능지표 파일(리포트/혼동행렬)을 스캔해 DB에 적재합니다."

    # 예: 250329_ATH@SEA_valid_report.txt
    #     250329_ATH@SEA_valid_confmat_Sigmoid.png
    #     250329_ATH@SEA_test_report.txt
    #     250329_ATH@SEA_test_confmat_Sigmoid.png
    PATTERN = re.compile(
        r"^(?P<date>\d{6})_(?P<away>[A-Za-z]+)@(?P<home>[A-Za-z]+)_(?P<split>valid|test)_(?P<kind>report|confmat)(?:_[A-Za-z0-9]+)?\.(?P<ext>txt|png)$"
    )

    def handle(self, *args, **options):
        base_dir = Path(settings.BASE_DIR) / "baseball_data" / "2025" / "web_data"
        if not base_dir.exists():
            self.stderr.write(f"❌ 경로 없음: {base_dir}")
            return

        buckets = {}  # key=(date_str, away, home)
        count_files = 0

        for p in base_dir.iterdir():
            if not p.is_file():
                continue
            m = self.PATTERN.match(p.name)
            if not m:
                continue
            count_files += 1
            date_str = m.group("date")
            away = m.group("away").upper()
            home = m.group("home").upper()
            split = m.group("split")       # valid | test
            kind = m.group("kind")         # report | confmat
            ext  = m.group("ext")          # txt | png

            key = (date_str, away, home)
            b = buckets.setdefault(key, {
                "date_str": date_str,
                "away": away,
                "home": home,
                "away_norm": normalize_code(away),
                "home_norm": normalize_code(home),
                "valid_report": None,
                "test_report": None,
                "valid_confmat_path": None,
                "test_confmat_path": None,
            })

            if kind == "report" and ext == "txt":
                # 텍스트 내용 읽어 저장
                try:
                    txt = p.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    txt = p.read_text(encoding="cp949", errors="ignore")
                if split == "valid":
                    b["valid_report"] = txt
                else:
                    b["test_report"] = txt

            elif kind == "confmat" and ext == "png":
                # 이미지 경로만 저장(실제 응답에서 파일 스트리밍)
                if split == "valid":
                    b["valid_confmat_path"] = str(p)
                else:
                    b["test_confmat_path"] = str(p)

        # upsert
        created, updated = 0, 0
        for key, rec in buckets.items():
            obj, is_created = MlbClassMetric.objects.update_or_create(
                date_str=rec["date_str"],
                away=rec["away"], home=rec["home"],
                defaults={
                    "away_norm": rec["away_norm"],
                    "home_norm": rec["home_norm"],
                    "valid_report": rec["valid_report"],
                    "test_report": rec["test_report"],
                    "valid_confmat_path": rec["valid_confmat_path"],
                    "test_confmat_path": rec["test_confmat_path"],
                }
            )
            created += 1 if is_created else 0
            updated += 0 if is_created else 1

        self.stdout.write(self.style.SUCCESS(
            f"📦 스캔 파일: {count_files}개 → upsert {len(buckets)}건 (created={created}, updated={updated})"
        ))
