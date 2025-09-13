# prediction/urls.py
from django.urls import path
from . import views

app_name = "prediction"

urlpatterns = [
    # 🔹 여기서는 league 세그먼트를 넣지 않습니다!
    path("prediction/", views.prediction, name="prediction"),

    # 상세(회귀 차트)
    path("prediction/<str:date_str>/<str:away>@<str:home>/",
         views.pred_detail, name="pred_detail"),

    # 분류 성능지표
    path("prediction/<str:date_str>/<str:away>@<str:home>/metrics/",
         views.class_metrics, name="class_metrics"),

    # 혼동행렬 이미지 스트리밍
    path("prediction/<str:date_str>/<str:away>@<str:home>/metrics/image/<str:which>/",
         views.class_metrics_image, name="class_metrics_image"),
]
