# views.py
from django.shortcuts import render
from datetime import date, timedelta, datetime
from calendar import monthrange
from match.models import Schedule


def schedule_list(request, league):
    request.session["league"] = league

    selected_date_str = request.GET.get("date")
    today = date.today()

    if selected_date_str:
        month, day = map(int, selected_date_str.split("/"))
        selected_date = date(today.year, month, day)
    else:
        selected_date = today

    # ✔ 해당 월 전체 날짜 리스트 만들기
    total_days = monthrange(selected_date.year, selected_date.month)[1]
    all_dates = [
        date(selected_date.year, selected_date.month, d)
        for d in range(1, total_days + 1)
    ]

    # ✔ 13일 단위로 끊어서 현재 날짜가 어느 chunk에 있는지 계산
    chunk_size = 13
    chunks = [
        all_dates[i : i + chunk_size] for i in range(0, len(all_dates), chunk_size)
    ]
    current_chunk = next(
        (chunk for chunk in chunks if selected_date in chunk), chunks[0]
    )

    # ✔ 이전/다음 chunk의 첫 날짜 계산
    current_index = chunks.index(current_chunk)

    if current_index > 0:
        prev_chunk_date = chunks[current_index - 1][0].strftime("%m/%d")
    else:
        prev_month_last_day = selected_date.replace(day=1) - timedelta(days=1)
        prev_chunk_date = prev_month_last_day.strftime("%m/%d")

    if current_index < len(chunks) - 1:
        next_chunk_date = chunks[current_index + 1][0].strftime("%m/%d")
    else:
        # 다음 달 첫 번째 날짜로 이동
        next_month_first_day = (
            selected_date.replace(day=1) + timedelta(days=32)
        ).replace(day=1)
        next_chunk_date = next_month_first_day.strftime("%m/%d")

    # ✔ 해당 날짜에 해당하는 경기만 가져오기
    # 🔸리그별 필터링 적용
    schedules = Schedule.objects.filter(
        league=league, month=selected_date.month, date=selected_date.day
    )

    available_dates = (
        Schedule.objects.filter(month=selected_date.month)
        .values_list("date", flat=True)
        .distinct()
    )
    available_dates = [
        f"{selected_date.month:02d}/{day:02d}" for day in available_dates
    ]

    context = {
        "schedules": schedules,
        "league": league,
        "year_month": f"{selected_date.year}.{selected_date.month}",
        "selected_date": selected_date.strftime("%m/%d"),
        "date_range": current_chunk,
        "prev_chunk_date": prev_chunk_date,
        "next_chunk_date": next_chunk_date,
        "schedules": schedules,
        "available_dates": available_dates,  # 경기 있는 경우 날짜 활성화
    }

    return render(request, "match/index.html", context)
