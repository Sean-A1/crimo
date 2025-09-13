# prediction/urls.py
from django.urls import path
from . import views

app_name = "prediction"

urlpatterns = [
    # 리스트(분류)
    path("", views.prediction, name="prediction"),

    # 상세(회귀 차트)
    path("<str:date_str>/<str:away>@<str:home>/", views.pred_detail, name="pred_detail"),

    # 분류 성능지표
    path("<str:date_str>/<str:away>@<str:home>/metrics/", views.class_metrics, name="class_metrics"),

    # 혼동행렬 이미지 스트리밍
    path("<str:date_str>/<str:away>@<str:home>/metrics/image/<str:which>/",
         views.class_metrics_image, name="class_metrics_image"),
    
    #  회귀 상세지표
    path("<str:date_str>/<str:away>@<str:home>/reg-metrics/", views.reg_metrics, name="reg_metrics"),
]