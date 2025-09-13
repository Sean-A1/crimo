# prediction/views.py
import os
from django.http import FileResponse, Http404
from django.shortcuts import render, get_object_or_404
from datetime import datetime, timedelta
from django.urls import reverse
from collections import defaultdict
from prediction.models import MlbPredClass, MlbPredReg, MlbClassMetric

def prediction(request, league=None):
    # 이번 페이지는 MLB 분류 전용 (상위 URL에서 넘어온 league 사용)
    league = (league or "mlb").lower()
    if league != "mlb":
        return render(request, "prediction/index.html", {
            "schedule_by_date": {},
            "week_range": "",
            "prev_week": "",
            "next_week": "",
            "league": league,
        })

    request.session["league"] = league

    selected_date_str = request.GET.get("date")  # "MM/DD"
    today = datetime.today()

    if selected_date_str:
        mm, dd = map(int, selected_date_str.split("/"))
        selected = datetime(today.year, mm, dd)
    else:
        latest = MlbPredClass.objects.order_by("-date").first()
        selected = datetime.combine(latest.date, datetime.min.time()) if latest else today

    weekday = selected.weekday()  # 0=Mon
    start_date = selected - timedelta(days=weekday)
    end_date = start_date + timedelta(days=6)

    qs = (MlbPredClass.objects
          .filter(date__range=[start_date.date(), end_date.date()])
          .order_by("date", "away_norm", "home_norm"))

    by_date = defaultdict(list)
    for o in qs:
        item = {
            "date": o.date,
            "month": o.date.month,
            "day": o.date.day,
            "date_str": f"{o.date.year%100:02d}{o.date.month:02d}{o.date.day:02d}",
            "away": o.away_norm,
            "home": o.home_norm,
            "away_pct": o.away_pct,
            "home_pct": o.home_pct,
        }
        key = f"{o.date.month:02d}/{o.date.day:02d}"
        by_date[key].append(item)

    context = {
        "schedule_by_date": dict(by_date),
        "week_range": f"{start_date.strftime('%b %d')} - {end_date.strftime('%d, %Y')}",
        "prev_week": (start_date - timedelta(days=7)).strftime("%m/%d"),
        "next_week": (start_date + timedelta(days=7)).strftime("%m/%d"),
        "league": league,
    }
    return render(request, "prediction/index.html", context)

def pred_detail(request, league=None, date_str=None, away=None, home=None):
    obj = get_object_or_404(
        MlbPredReg,
        date_str=date_str,
        away_norm=(away or "").upper(),
        home_norm=(home or "").upper(),
    )

    # 예측 이닝
    pred_away, pred_home = obj.pred_lists()

    # 실제 이닝 (없으면 빈 배열)
    act_away = obj._split_nums(obj.act_inn_away or "")
    act_home = obj._split_nums(obj.act_inn_home or "")

    ctx = {
        "league": (league or "mlb").lower(),
        "date_str": date_str,
        "away": obj.away_norm,
        "home": obj.home_norm,
        "scenario_team1": pred_away,   # away (예측)
        "scenario_team2": pred_home,   # home (예측)
        "actual_team1": act_away,      # away (실제)
        "actual_team2": act_home,      # home (실제)
        "date": obj.date,
    }
    return render(request, "prediction/detail/index.html", ctx)

def class_metrics(request, league, date_str, away, home):
    """
    분류 성능지표 페이지. 텍스트/이미지 순서:
    1) valid_report.txt
    2) valid_confmat.png
    3) test_report.txt
    4) test_confmat.png
    """
    obj = (
        MlbClassMetric.objects.filter(
            date_str=date_str,
            away_norm=away.upper(), home_norm=home.upper()
        ).first()
        or
        MlbClassMetric.objects.filter(
            date_str=date_str,
            away=away.upper(), home=home.upper()
        ).first()
    )
    if not obj:
        raise Http404("성능지표가 없습니다.")

    ctx = {
        "league": league,
        "date_str": date_str,
        "away": obj.away_norm,
        "home": obj.home_norm,
        "valid_report": obj.valid_report,
        "test_report": obj.test_report,
        "valid_img_url": reverse("prediction:class_metrics_image",
                                 args=[league, date_str, obj.away_norm, obj.home_norm, "valid"]),
        "test_img_url": reverse("prediction:class_metrics_image",
                                args=[league, date_str, obj.away_norm, obj.home_norm, "test"]),
    }
    return render(request, "prediction/detail/metrics.html", ctx)


def class_metrics_image(request, league, date_str, away, home, which):
    """
    혼동행렬 PNG 스트리밍. which ∈ {"valid","test"}
    """
    rec = (
        MlbClassMetric.objects.filter(
            date_str=date_str, away_norm=away.upper(), home_norm=home.upper()
        ).first()
        or
        MlbClassMetric.objects.filter(
            date_str=date_str, away=away.upper(), home=home.upper()
        ).first()
    )
    if not rec:
        raise Http404("지표 파일이 없습니다.")

    path = rec.valid_confmat_path if which == "valid" else rec.test_confmat_path
    if not path or not os.path.exists(path):
        raise Http404("이미지 파일을 찾을 수 없습니다.")

    return FileResponse(open(path, "rb"), content_type="image/png")

def reg_metrics(request, league, date_str, away, home):
    obj = get_object_or_404(
        MlbPredReg,
        date_str=date_str,
        away_norm=away.upper(),
        home_norm=home.upper(),
    )

    # 투수교체 리스트: " | " 기준 분리
    changes_list = []
    if obj.pitching_changes:
        # 안전하게 파이프 기준으로 split
        changes_list = [seg.strip() for seg in obj.pitching_changes.split("|") if seg.strip()]

    ctx = {
        "league": league,
        "date_str": date_str,
        "away": obj.away_norm,
        "home": obj.home_norm,
        "actual_starters": obj.actual_starters or "정보 없음",
        "predicted_starters": obj.predicted_starters or "정보 없음",
        "pitching_changes_list": changes_list,  # 리스트 렌더
        "game_pk": obj.game_pk,
        "date": obj.date,
        # 점수 합계가 있으면 같이 보여주면 좋음
        "pred_total": (obj.pred_total_away, obj.pred_total_home),
        "act_total": (obj.act_total_away, obj.act_total_home),
    }
    return render(request, "prediction/detail/reg_metrics.html", ctx)