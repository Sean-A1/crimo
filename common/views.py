from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from common.forms import UserForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from pybo.models import Question, Answer  # 작성한 질문/답변 조회 용

from datetime import datetime
from match.models import Schedule
from django.db.models import Q

import json
from django.http import HttpResponse


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

    request.session["league"] = league
    main_event = Schedule.objects.filter(league=league, is_main_event=True).first()

    # 시나리오 정수 리스트로 변환
    scenario_team1 = []
    scenario_team2 = []

    if main_event and main_event.scenario_team1 and main_event.scenario_team2:
        try:
            scenario_team1 = list(
                map(float, main_event.scenario_team1.strip().split(";"))
            )
            scenario_team2 = list(
                map(float, main_event.scenario_team2.strip().split(";"))
            )
        except Exception:
            scenario_team1, scenario_team2 = [], []

    context = {
        "league": league,
        "main_event": main_event,
        "scenario_team1": json.dumps(scenario_team1),
        "scenario_team2": json.dumps(scenario_team2),
    }

    return render(request, f"common/league_home_{league}.html", context)


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
