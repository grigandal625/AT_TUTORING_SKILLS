from django.contrib import admin

# Register your models here.
from .models import Task, Skill, Reaction, ScenarioPart, Event

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('task_name', 'description', 'on_success', 'on_failure')
    search_fields = ('task_name',)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'scenario_name')
    search_fields = ('name',)

@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'message')

@admin.register(ScenarioPart)
class ScenarioPartAdmin(admin.ModelAdmin):
    list_display = ('scenario_id', 'task_id', 'order')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'description', 'task_id')
    search_fields = ('event_name', 'task_id')
