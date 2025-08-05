from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    #게시판(카테고리) 분류를 나타내는 모델
    
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200, blank=True, null=True)
    has_answer = models.BooleanField(default=True)
    # has_answer=True 이면 '질문+답변' 형태 게시판, False면 단순 게시판
    # 필요에 따라 다른 속성(순서, 접근권한 등)도 추가할 수 있음

    def __str__(self):
        return self.name

class Question(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_question')
    # some_user.author_question.all()
    
    subject = models.CharField(max_length=200)
    content = models.TextField()
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)   
    # 질문이나 답변이 언제 수정되었는지
    # null=True는 데이터베이스에서 modify_date 칼럼에 null을 허용
    # blank=True는 form.is_valid()를 통한 입력 데이터 검증 시 값이 없어도 된다는 의미
    # null=True, blank=True는 어떤 조건으로든 값을 비워둘 수 있음을 의미
    
    voter = models.ManyToManyField(User, related_name='voter_question')
    
    # 새로 추가된 필드: 어떤 카테고리에 속한 질문인지 지정
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='question_set',
        null=True,
        blank=True
    )
    
    view_count = models.IntegerField(default=0)  # 조회수 기본값 0
    
    def __str__(self):
        return self.subject


class Answer(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_answer')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.TextField()
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True) # 질문이나 답변이 언제 수정되었는지
    voter = models.ManyToManyField(User, related_name='voter_answer')
    
    def __str__(self):
       # 질문과 구분하기 위해 일부분만 표시하거나,
       # "답변: {self.content[:20]}..." 식으로 짧게 보여줄 수도 있음
       return f"Answer to: {self.question.subject}"
   
class QuestionCount(models.Model):
    """
    동일 IP에서 한 번만 조회수를 늘리기 위해, 
    어떤 IP가 어떤 Question을 조회했는지 기록.
    """
    ip = models.CharField(max_length=30)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.ip} - {self.question.subject}"