import csv
import os
from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from team.models import Team, Player


class Command(BaseCommand):
    help = "CSV 파일에서 연도별 선수 데이터를 불러옵니다."

    def handle(self, *args, **kwargs):
        base_dir = os.path.join(settings.BASE_DIR, "baseball_data")
        if not os.path.exists(base_dir):
            self.stderr.write("❌ baseball_data 디렉토리가 존재하지 않습니다.")
            return

        for year_folder in os.listdir(base_dir):
            if not year_folder.isdigit():
                continue
            year = int(year_folder)

            for league in ["kbo", "mlb"]:
                file_path = os.path.join(base_dir, year_folder, f"{league}_player.csv")

                if not os.path.exists(file_path):
                    self.stdout.write(
                        f"📁 {year} {league.upper()} player.csv 없음 → 건너뜀"
                    )
                    continue

                # 기존 데이터 삭제
                Player.objects.filter(team__league=league).delete()
                Team.objects.filter(league=league).delete()

                try:
                    with open(file_path, newline="", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if not row.get("player_id") or not row.get("birthday"):
                                self.stderr.write(f"❗ 필수 정보 누락 → 건너뜀: {row}")
                                continue

                            team_key = row.get("team_id") or row.get("team")
                            if not team_key:
                                self.stderr.write(f"❌ 팀 정보 누락: {row}")
                                continue
                            team_id = team_key.strip()

                            team, created = Team.objects.get_or_create(
                                team_id=team_id,
                                defaults={
                                    "league": league,
                                    "logo": f"team_logos/{league}/{team_id}.png",
                                },
                            )

                            if not created:
                                if not team.league:
                                    team.league = league
                                if not team.logo:
                                    team.logo = f"team_logos/{league}/{team_id}.png"
                                team.save()

                            try:
                                birthday = datetime.strptime(
                                    row["birthday"], "%m/%d/%Y"
                                ).date()
                            except ValueError:
                                self.stderr.write(
                                    f"❗ 생일 형식 오류 → {row['birthday']}"
                                )
                                continue

                            Player.objects.update_or_create(
                                player_id=row["player_id"],
                                defaults={
                                    "backnumber": (
                                        int(row["backnumber"])
                                        if row.get("backnumber")
                                        else None
                                    ),
                                    "team": team,
                                    "position": row.get("position", ""),
                                    "birthday": birthday,
                                    "profile": row.get("profile", ""),
                                    
                                
                                    
                                },
                            )

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ {year} {league.upper()} 선수 불러오기 완료"
                        )
                    )

                except Exception as e:
                    self.stderr.write(
                        self.style.ERROR(
                            f"❌ {year} {league.upper()} 처리 중 오류 발생: {e}"
                        )
                    )