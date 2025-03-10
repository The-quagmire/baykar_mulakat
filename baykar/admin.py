from django.contrib import admin
from .models import Team, Personnel, Part, Aircraft

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'team_type')
    search_fields = ('name',)
    list_filter = ('team_type',)

@admin.register(Personnel)
class PersonnelAdmin(admin.ModelAdmin):
    list_display = ('user', 'team')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    list_filter = ('team',)

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ('name', 'part_type', 'aircraft_type', 'is_used', 'produced_by', 'production_date')
    search_fields = ('name',)
    list_filter = ('part_type', 'aircraft_type', 'is_used', 'produced_by')

@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    list_display = ('name', 'aircraft_type', 'assembled_by', 'assembly_date')
    search_fields = ('name',)
    list_filter = ('aircraft_type', 'assembled_by')

