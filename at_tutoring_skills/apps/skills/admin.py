from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Skill
from .models import SKillConnection
from .models import Task
from .models import TaskUser
from .models import User
from .models import UserSkill
from .models import Variant


@admin.register(Skill)
class SkillAdmin(ModelAdmin):
    list_display = ("id", "name", "get_group_display", "code")
    list_filter = ("group",)
    search_fields = ("name",)
    list_select_related = ("variant",)

    def get_group_display(self, obj):
        return obj.get_group_display()

    get_group_display.short_description = "Group"


@admin.register(SKillConnection)
class SKillConnectionAdmin(ModelAdmin):
    list_display = ("id", "skill_from", "skill_to", "weight")
    search_fields = ("skill_from__name", "skill_to__name")


@admin.register(Task)
class TaskAdmin(ModelAdmin):
    list_display = ("id", "task_name", "get_task_object_display", "object_name")
    list_filter = ("task_object",)
    search_fields = ("task_name", "object_name")
    filter_horizontal = ("skills",)

    def get_task_object_display(self, obj):
        return obj.get_task_object_display()

    get_task_object_display.short_description = "Task Object"


@admin.register(Variant)
class VariantAdmin(ModelAdmin):
    list_display = ("id", "name", "display_tasks")
    search_fields = ("name",)
    # filter_horizontal = ("task",)

    def display_tasks(self, obj):
        return ", ".join([task.task_name for task in obj.task.all()])

    display_tasks.short_description = "Tasks"


@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = ("user_id", "variant")
    search_fields = ("user_id",)
    list_select_related = ("variant",)


@admin.register(TaskUser)
class TaskUserAdmin(ModelAdmin):
    list_display = ("id", "user", "task", "attempts", "is_completed")
    list_filter = ("is_completed", "task__task_name")
    search_fields = ("user__user_id", "task__task_name")
    list_select_related = ("user", "task")
    raw_id_fields = ("user", "task")


@admin.register(UserSkill)
class UserSkillAdmin(ModelAdmin):
    list_display = ("id", "user", "skill", "is_completed")
    list_filter = ("is_completed", "skill__name")
    search_fields = ("user__user_id", "skill__name")
    list_select_related = ("user", "skill")
    raw_id_fields = ("user", "skill")


# Если нужно зарегистрировать выборки как модели (хотя обычно это не нужно)
# admin.site.register(SUBJECT_CHOICES)
# admin.site.register(GROUP_CHOICES)
