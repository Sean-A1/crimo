FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 의존성 먼저 복사
COPY requirements.txt .

# .sh 파일 실행 권한
COPY .devcontainer/entrypoint.sh .devcontainer/entrypoint.sh
RUN chmod +x .devcontainer/entrypoint.sh

# 의존성 설치
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 전체 소스 복사 (한 번만!)
COPY . .

# logs 디렉토리 생성
RUN mkdir -p logs

# Django 환경 설정
ENV DJANGO_SETTINGS_MODULE=config.settings.local

# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
