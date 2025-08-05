from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from datetime import datetime, timedelta
from match.models import Schedule
import json


def prediction(request, league):
    request.session["league"] = league
    selected_date_str = request.GET.get("date")
    today = datetime.today()

    if selected_date_str:
        month, day = map(int, selected_date_str.split("/"))
        selected_date = datetime(today.year, month, day)
    else:
        selected_date = today

    # ✅ 월요일 기준으로 시작 (weekday: 0=월, 6=일)
    weekday = selected_date.weekday()
    days_since_monday = weekday
    start_date = selected_date - timedelta(days=days_since_monday)
    end_date = start_date + timedelta(days=6)  # 월~일

    # 📌 리그 일정 가져와 날짜로 필터
    all_schedules = Schedule.objects.filter(league=league)

    filtered_schedules = []
    for schedule in all_schedules:
        try:
            game_date = datetime(today.year, schedule.month, schedule.date)
            if start_date <= game_date <= end_date:
                filtered_schedules.append(schedule)
        except Exception:
            continue

    # 📌 날짜별 그룹화
    schedule_by_date = {}
    for schedule in filtered_schedules:
        date_str = f"{schedule.month}/{schedule.date}"
        schedule_by_date.setdefault(date_str, []).append(schedule)

    context = {
        "schedule_by_date": schedule_by_date,
        "week_range": f"{start_date.strftime('%b %d')} - {end_date.strftime('%d, %Y')}",
        "prev_week": (start_date - timedelta(days=7)).strftime("%m/%d"),
        "next_week": (start_date + timedelta(days=7)).strftime("%m/%d"),
        "league": league,
    }

    return render(request, "prediction/index.html", context)


def pred_detail(request, league, month, date, team1, team2):
    schedule = get_object_or_404(
        Schedule, month=month, date=date, team1=team1, team2=team2
    )

    scenario_team1 = list(map(int, schedule.scenario_team1.split(";")))
    scenario_team2 = list(map(int, schedule.scenario_team2.split(";")))

    context = {
        "schedule": schedule,
        "scenario_team1": json.dumps(scenario_team1),
        "scenario_team2": json.dumps(scenario_team2),
        "league": schedule.league,
    }

    return render(request, "prediction/detail/index.html", context)
