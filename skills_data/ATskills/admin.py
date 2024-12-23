from django.contrib import admin

# Register your models here.
from .models import Task, Skill, Reaction

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
