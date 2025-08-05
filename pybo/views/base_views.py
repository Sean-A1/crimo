from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count

from ..models import Question, QuestionCount

import logging
# logger = logging.getLogger('pybo')
logger = logging.getLogger(__name__)

def index(request):
    logger.info("INFO 레벨로 출력")
    page = request.GET.get('page', '1')  # 페이지
    kw = request.GET.get('kw', '')  # 검색어
    question_list = Question.objects.order_by('-create_date')
    
    if kw:
        question_list = question_list.filter(
            Q(subject__icontains=kw) |  # 제목 검색
            Q(content__icontains=kw) |  # 내용 검색
            Q(answer__content__icontains=kw) |  # 답변 내용 검색
            Q(author__username__icontains=kw) |  # 질문 글쓴이 검색
            Q(answer__author__username__icontains=kw)  # 답변 글쓴이 검색
        ).distinct()
        
    paginator = Paginator(question_list, 10)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)
    context = {'question_list': page_obj, 'page': page, 'kw': kw}
    return render(request, 'pybo/question_list.html', context)

def detail(request, question_id):
    # 1) 질문 객체 가져오기
    question = get_object_or_404(Question, pk=question_id)
    
    # --------------------
    # 조회수 로직 (동일 IP 중복 방지)
    # --------------------
    client_ip = get_client_ip(request)
    # 해당 (ip, question) 쌍이 이미 존재하는지 체크
    cnt = QuestionCount.objects.filter(ip=client_ip, question=question).count()

    if cnt == 0:
        # 처음 방문이므로 기록을 남기고, 조회수 증가
        QuestionCount.objects.create(ip=client_ip, question=question)
        question.view_count += 1
        question.save()
    
    
    # 2) GET 파라미터로 'sort'와 'page' 받기
    sort = request.GET.get('sort', 'voter')  # 기본 정렬 기준: 추천순
    page = request.GET.get('page', '1')      # 기본 페이지: 1

    # 3) 답변 목록 정렬
    if sort == 'recent':
        # 최신순 정렬
        answer_list = question.answer_set.order_by('-create_date')
    else:
        # 추천순 정렬 (voter_count 많을수록 먼저, tie-breaker로 create_date 내림차순)
        # 'voter_count'라는 임시 필드를 만들어 정렬
        answer_list = question.answer_set \
                              .annotate(voter_count=Count('voter')) \
                              .order_by('-voter_count', '-create_date')

    # 4) 페이지네이션
    paginator = Paginator(answer_list, 5)  # 페이지당 5개씩 (원하는 대로 조절)
    page_obj = paginator.get_page(page)

    # 5) 템플릿에 필요한 데이터 구성
    context = {
        'question': question,
        'answer_list': page_obj,  # 페이징된 답변 리스트
        'page': page,
        'sort': sort,
    }
    return render(request, 'pybo/question_detail.html', context)

def get_client_ip(request):
    """사용자의 IP 주소를 반환하는 함수"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip