from django.urls import path
from . import views

app_name = 'prediction'

urlpatterns = [
    path('prediction/', views.prediction, name='prediction'),
    path('<int:month>/<int:date>/<str:team1>/<str:team2>/', views.pred_detail, name='pred_detail'),
]
