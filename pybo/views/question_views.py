from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from ..forms import QuestionForm
from ..models import Question


@login_required(login_url='common:login') 
def question_create(request):
    if request.method == 'POST': # 항목 저장 (저장하기): POST
        form = QuestionForm(request.POST) # request.POST에 담긴 subject와 content 값이 QuestionForm의 subject와 content 속성에 자동으로 매핑
        if form.is_valid():  # 폼이 유효하다면 (subject, content 값 검사)
            question = form.save(commit=False)  # 폼에 저장된 데이터로 Question 데이터를 생성
            # commit=False 는 임시 저장. 현재 subject와 content 속성만 정의되어 있고, create_date 속성은 포함되지 않았다. 아래 줄에서 따로 저장
            
            question.author = request.user  # author 속성에 로그인 계정 저장
            question.create_date = timezone.now()  # 실제 저장을 위해 작성일시를 설정한다.
            question.save()  # 데이터를 실제로 저장한다.
            return redirect('pybo:index')
    else: # 링크를 통해 페이지를 요청 (질문 등록): GET
        form = QuestionForm()
    context = {'form': form}
    return render(request, 'pybo/question_form.html', context)

@login_required(login_url='common:login') 
def question_modify(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.user != question.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('pybo:detail', question_id=question.id)
    if request.method == "POST": # 질문 수정 화면에서 "저장하기" 버튼을 클릭하면 페이지가 POST 방식으로 호출
        #form 태그에 action 속성이 없는 경우 디폴트 action은 현재 페이지
        
        form = QuestionForm(request.POST, instance=question) 
        # POST 요청인 경우 수정된 내용을 반영해야 하는 케이스
        # instance를 기준으로 QuestionForm을 생성하지만 request.POST의 값으로 덮어쓰라는 의미
        # 질문 수정화면에서 제목 또는 내용을 변경하여 POST 요청하면 변경된 내용이 QuestionForm에 저장
        
        if form.is_valid():
            question = form.save(commit=False)
            question.modify_date = timezone.now()  # 수정일시 현재일시로 저장
            question.save()
            return redirect('pybo:detail', question_id=question.id)
    else:
        form = QuestionForm(instance=question)
        # instance 값을 지정하면 폼의 속성 값이 instance의 값으로 채워진다. 따라서 질문을 수정하는 화면에서 제목과 내용이 채워진 채로 보일 것이다.
    context = {'form': form}
    return render(request, 'pybo/question_form.html', context)

@login_required(login_url='common:login') 
def question_delete(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.user != question.author:
        messages.error(request, '삭제권한이 없습니다')
        return redirect('pybo:detail', question_id=question.id)
    question.delete()
    return redirect('pybo:index')

@login_required(login_url='common:login')
def question_vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.user == question.author:
        messages.error(request, '본인이 작성한 글은 추천할수 없습니다')
    else:
        question.voter.add(request.user)
    return redirect('pybo:detail', question_id=question.id)