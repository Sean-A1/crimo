from django.contrib import admin
from .models import Schedule

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['month', 'date', 'day', 'team1', 'score_team1', 'team2', 'score_team2', 'stadium', 'time', 'is_main_event']
    list_filter = ['league', 'is_main_event', 'month', 'day', 'team1', 'team2']
    list_editable = ['is_main_event', 'score_team1', 'score_team2']
    search_fields = ['team1', 'team2', 'stadium']
