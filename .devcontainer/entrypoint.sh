#!/bin/bash

mkdir -p db logs
touch logs/logs.log

python manage.py makemigrations
python manage.py migrate
python manage.py import_players
python manage.py import_schedules
python manage.py import_prediction_mlb_classification
python manage.py import_prediction_mlb_regression
python manage.py import_prediction_mlb_metrics

# superuser 자동 생성 with 확인 메시지
echo "🛠 Superuser 생성 시도..."

python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', '1111')
    print('✅ Superuser 생성 완료')
else:
    print('ℹ️ Superuser 이미 존재함')
"

echo "✅ 초기 설정 완료"
