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
                Schedule.objects.filter(league=league, year=year).delete()

                schedules = []

                # ✅ 기존 데이터 삭제 (중요!)
                Schedule.objects.filter(league=league).delete()

                with open(file_path, newline="", encoding="utf-8-sig") as csvfile:
                    reader = csv.DictReader(
                        csvfile,
                        fieldnames=[
                            "날짜",
                            "시간",
                            "경기",
                            "구장",
                            "예측_승패",
                            "득점0",
                            "득점1",
                            "예측_시나리오0",
                            "예측_시나리오1",
                        ],
                    )
                    next(reader)

                    for row in reader:
                        try:
                            date_match = re.match(r"(\d+)\.(\d+)\((.+)\)", row["날짜"])
                            if not date_match:
                                self.stderr.write(f"날짜 형식 오류: {row['날짜']}")
                                continue
                            month, date, day = date_match.groups()

                            teams = row["경기"].split("vs")
                            if len(teams) != 2:
                                self.stderr.write(f"경기 데이터 오류: {row['경기']}")
                                continue
                            team1, team2 = teams

                            predict_win_match = row["예측_승패"].split(";")
                            if len(predict_win_match) != 2:
                                win_prob_team1, win_prob_team2 = 0, 0
                            else:
                                win_prob_team1, win_prob_team2 = map(
                                    int, predict_win_match
                                )

                            schedule = Schedule(
                                year=year,
                                month=int(month),
                                date=int(date),
                                day=day.strip(),
                                time=row["시간"].strip(),
                                stadium=row["구장"].strip(),
                                team1=team1.strip(),
                                team2=team2.strip(),
                                win_prob_team1=win_prob_team1,
                                win_prob_team2=win_prob_team2,
                                score_team1=row["득점0"],
                                score_team2=row["득점1"],
                                scenario_team1=row["예측_시나리오0"].strip(),
                                scenario_team2=row["예측_시나리오1"].strip(),
                                league=league,
                            )
                            schedules.append(schedule)

                        except Exception as e:
                            self.stderr.write(f"오류 발생: {row} - {e}")

                Schedule.objects.bulk_create(schedules)
                self.stdout.write(
                    self.style.SUCCESS(f"✅ {league.upper()} {year} 일정 불러오기 완료")
                )
