# prod dockerfile

FROM python:3.12-slim

# 환경 변수
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.prod

# 작업 디렉토리
WORKDIR /app

# 시스템 패키지 업데이트 & Pillow 등 이미지 처리를 위한 의존성 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 의존성 먼저 복사 (빌드 캐시 최적화)
COPY requirements.txt .

# pip 업그레이드 및 의존성 설치
RUN pip install --upgrade pip && pip install -r requirements.txt

# 소스 전체 복사
COPY . .

# logs, db 디렉토리 보장
RUN mkdir -p /app/logs /app/db

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
