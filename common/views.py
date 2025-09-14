import json
from datetime import datetime

from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from common.forms import UserForm
from match.models import Schedule
from django.db.models import Q, Exists, OuterRef
from prediction.models import MlbPredReg, MlbPredClass, normalize_code
from pybo.models import Question, Answer

def home(request):
    today = datetime.today()

    schedules_today = Schedule.objects.filter(month=today.month, date=today.day)

    if schedules_today.exists():
        display_date = today.strftime("%m/%d")
        schedules = schedules_today
    else:
        next_game = (
            Schedule.objects.filter(
                Q(month__gt=today.month) | Q(month=today.month, date__gt=today.day)
            )
            .order_by("month", "date")
            .first()
        )

        if next_game:
            display_date = f"{next_game.month}/{next_game.date}"
            schedules = Schedule.objects.filter(
                month=next_game.month, date=next_game.date
            )
        else:
            display_date = "경기 없음"
            schedules = []

    context = {"schedules": schedules, "display_date": display_date}

    return render(request, "common/home.html", context)


def home1(request):
    return render(request, "common/home1.html")


def league_home(request, league):
    if league == "favicon.ico":
        return HttpResponse(status=204)

    league = (league or "").lower()
    request.session["league"] = league
    today = datetime.today().date()

    # ── 공통: class가 존재하는 reg만 고르는 서브쿼리
    cls_exists = Exists(
        MlbPredClass.objects.filter(
            date=OuterRef("date"),
            away_norm=OuterRef("away_norm"),
            home_norm=OuterRef("home_norm"),
        )
    )

    reg = None
    cls = None
    sched = (
        Schedule.objects
        .filter(league=league, is_main_event=True)
        .order_by("-month", "-date", "-id")
        .first()
    )

    # 1) 관리자 선택 경기 우선(양쪽 다 있어야 함)
    if sched:
        a = normalize_code((sched.team1 or "").upper())
        h = normalize_code((sched.team2 or "").upper())

        reg = (
            MlbPredReg.objects
            .annotate(has_cls=cls_exists)
            .filter(date__month=sched.month, date__day=sched.date,
                    away_norm=a, home_norm=h, has_cls=True)
            .order_by("-date").first()
        ) or (
            # 혹시 팀 표기가 뒤집힌 경우도 허용
            MlbPredReg.objects
            .annotate(has_cls=cls_exists)
            .filter(date__month=sched.month, date__day=sched.date,
                    away_norm=h, home_norm=a, has_cls=True)
            .order_by("-date").first()
        )

        if reg:
            cls = (
                MlbPredClass.objects
                .filter(date=reg.date, away_norm=reg.away_norm, home_norm=reg.home_norm)
                .first()
            )

    # 2) 관리자 선택이 없거나 매칭 실패면 → 오늘 기준 가장 가까운 경기(미래 우선, 없으면 과거), 단 reg+class 둘 다 있는 것만
    if not reg and league == "mlb":
        reg = (
            MlbPredReg.objects
            .annotate(has_cls=cls_exists)
            .filter(has_cls=True, date__gte=today)
            .order_by("date").first()
        ) or (
            MlbPredReg.objects
            .annotate(has_cls=cls_exists)
            .filter(has_cls=True, date__lt=today)
            .order_by("-date").first()
        )
        if reg:
            cls = (
                MlbPredClass.objects
                .filter(date=reg.date, away_norm=reg.away_norm, home_norm=reg.home_norm)
                .first()
            )

    # 3) 화면 데이터 구성
    if reg and cls:
        pred_away, pred_home = reg.pred_lists()
        act_away = reg._split_nums(reg.act_inn_away or "")
        act_home = reg._split_nums(reg.act_inn_home or "")

        # 선택된 sched가 없을 수도 있으니 안전하게
        time_txt = getattr(sched, "time", "") if sched else ""
        stadium_txt = getattr(sched, "stadium", "") if sched else ""

        main_event = {
            "league": league,
            "month": reg.date.month,
            "date": reg.date.day,
            "day": reg.date.strftime("%a"),
            "time": time_txt,
            "stadium": stadium_txt,
            "team1": reg.away_norm,   # 왼쪽: AWAY
            "team2": reg.home_norm,   # 오른쪽: HOME
            "win_prob_team1": cls.away_pct,
            "win_prob_team2": cls.home_pct,
            "scenario_team1": pred_away,
            "scenario_team2": pred_home,
            "actual_team1": act_away,
            "actual_team2": act_home,
            "date_str": reg.date_str,
            "has_pred": True,
        }
    else:
        main_event = {
            "league": league,
            "month": "", "date": "", "day": "",
            "time": "", "stadium": "",
            "team1": "", "team2": "",
            "win_prob_team1": None, "win_prob_team2": None,
            "scenario_team1": [], "scenario_team2": [],
            "actual_team1": [], "actual_team2": [],
            "date_str": "",
            "has_pred": False,
        }

    return render(request, f"common/league_home_{league}.html", {
        "league": league,
        "main_event": main_event,
    })



def set_league(request, league_name):
    if league_name in ["kbo", "mlb"]:
        request.session["league"] = league_name
    return redirect("home1")


def logout_view(request):
    logout(request)
    return redirect("home")


def signup(request):
    if (
        request.method == "POST"
    ):  # POST 요청인 경우에는 화면에서 입력한 데이터로 사용자를 생성
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            # form.cleaned_data.get은 폼의 입력값을 개별적으로 얻고 싶은 경우에 사용하는 함수
            # 이 경우 폼의 입력값은 인증시 사용할 사용자명과 비밀번호

            # 신규 사용자를 생성한 후에 자동 로그인
            user = authenticate(username=username, password=raw_password)  # 사용자 인증
            login(request, user)  # 로그인
            return redirect("home")
    else:  # GET 요청인 경우에는 회원가입 화면을 보여준다
        form = UserForm()
    return render(request, "common/signup.html", {"form": form})


@login_required
def profile(request):
    """
    로그인한 사용자 본인의 프로필(마이페이지).
    닉네임, 이메일, 가입일, 작성 질문/답변 등 표시
    """
    user = request.user  # 현재 로그인한 User 객체
    # 작성한 질문 목록
    question_list = Question.objects.filter(author=user).order_by("-create_date")
    # 작성한 답변 목록
    answer_list = Answer.objects.filter(author=user).order_by("-create_date")

    context = {
        "user": user,
        "question_list": question_list,
        "answer_list": answer_list,
    }
    return render(request, "common/profile.html", context)
