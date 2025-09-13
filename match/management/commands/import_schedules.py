import csv
import os
import re
from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from match.models import Schedule


class Command(BaseCommand):
    help = "CSV 파일에서 경기 일정 데이터를 연도별로 자동 불러옵니다."

    def handle(self, *args, **kwargs):
        base_path = settings.BASE_DIR / "baseball_data"
        
        if not os.path.exists(base_path):
            self.stderr.write("❌ baseball_data 디렉토리가 없습니다.")
            return

        def _parse_score(val: str):
            """'-' 또는 빈칸이면 None, 숫자면 int로 변환. 이상값도 최대한 숫자만 추출."""
            if val is None:
                return None
            s = str(val).strip()
            if s == "" or s == "-":
                return None
            try:
                return int(s)
            except ValueError:
                m = re.search(r"\d+", s)
                return int(m.group()) if m else None

        for year_folder in os.listdir(base_path):
            if not year_folder.isdigit():
                continue
            
            year = int(year_folder)
            year_path = base_path / year_folder

            for league in ["kbo", "mlb"]:
                file_path = year_path / f"{league}_schedule.csv"
                if not file_path.exists():
                    self.stderr.write(f"❌ 파일 없음: {file_path}")
                    continue

                self.stdout.write(f"📥 {league.upper()} {year} 일정 가져오는 중...")
                
                # 해당 연도+리그만 정리
                Schedule.objects.filter(league=league, year=year).delete()

                schedules = []

                # ✅ 기존 데이터 삭제 (중요!)
                Schedule.objects.filter(league=league).delete()

                with open(file_path, newline="", encoding="utf-8-sig") as csvfile:
                    # 헤더 자동 인식 (한국어 헤더 그대로 사용)
                    reader = csv.DictReader(csvfile)
                    '''
                    reader = csv.DictReader(
                        csvfile,
                        fieldnames=[
                            "날짜",
                            "시간",
                            "경기",
                            "구장",
                            "득점0",
                            "득점1",
                        ],
                    )
                    next(reader)
                    '''

                    for row in reader:
                        try:
                            raw_date = (row.get("날짜") or "").strip()
                            raw_time = (row.get("시간") or "").strip()
                            raw_game = (row.get("경기") or "").strip()
                            raw_stadium = (row.get("구장") or "").strip()
                            raw_s0 = row.get("득점0")
                            raw_s1 = row.get("득점1")

                            # 날짜: "MM.DD(Day)" 형식
                            m = re.match(r"(\d+)\.(\d+)\(([^)]+)\)", raw_date)
                            if not m:
                                self.stderr.write(f"⚠️ 날짜 형식 오류 → {raw_date}")
                                continue
                            month, date, day = m.groups()

                            # 경기: "AAAvsBBB"
                            parts = raw_game.split("vs")
                            if len(parts) != 2:
                                self.stderr.write(f"⚠️ 경기 데이터 오류 → {raw_game}")
                                continue
                            team1, team2 = parts[0].strip(), parts[1].strip()

                            # 득점 파싱 ('-' → None)
                            score_team1 = _parse_score(raw_s0)
                            score_team2 = _parse_score(raw_s1)

                            schedules.append(
                                Schedule(
                                    year=year,
                                    month=int(month),
                                    date=int(date),
                                    day=day.strip(),
                                    time=raw_time,  # 문자열로 그대로 저장
                                    team1=team1,
                                    team2=team2,
                                    stadium=raw_stadium,
                                    score_team1=score_team1,
                                    score_team2=score_team2,
                                    league=league,
                                )
                            )
                        except Exception as e:
                            self.stderr.write(f"❗ 오류 발생: {row} - {e}")

                if schedules:
                    Schedule.objects.bulk_create(schedules, batch_size=1000)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ {league.upper()} {year} 일정 불러오기 완료 (총 {len(schedules)}건)"
                    )
                )