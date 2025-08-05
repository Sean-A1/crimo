# team/admin.py
from django.contrib import admin
from .models import Team, Player

class PlayerAdmin(admin.ModelAdmin):
    list_display = ('player_id', 'backnumber', 'team', 'position', 'birthday')

class TeamAdmin(admin.ModelAdmin):
    list_display = ('team_id', 'name', 'logo')

admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
