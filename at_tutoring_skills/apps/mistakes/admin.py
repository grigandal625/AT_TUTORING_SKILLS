from django.contrib import admin
from django.contrib.admin import ModelAdmin, TabularInline
from at_tutoring_skills.apps.mistakes.models import Mistake, MISTAKE_TYPE_CHOICES

# class SkillInline(TabularInline):
#     model = Mistake.skills.through  # Используем through модель для ManyToMany
#     extra = 1
#     verbose_name = "Связанный навык"
#     verbose_name_plural = "Связанные навыки"
class SkillInline(TabularInline):
    model = Mistake.skills.through  # Используем through модель для ManyToMany
    extra = 1
    verbose_name = "Связанный навык"
    verbose_name_plural = "Связанные навыки"

@admin.register(Mistake)
class MistakeAdmin(ModelAdmin):
    list_display = (
        'id',
        'get_user_id',
        'get_mistake_type_display',
        'get_task_name',
        'fine',
        'is_tip_shown',
        'skills_list'
    )
    list_filter = (
        'mistake_type',
        'is_tip_shown',
        ('skills', admin.RelatedOnlyFieldListFilter),
    )
    search_fields = (
        'user__user_id',
        'task__task_name',
        'tip',
    )
    raw_id_fields = ('user', 'task')
    exclude = ('skills',)  # Скрываем стандартное поле, используем inline
    inlines = (SkillInline,)
    list_per_page = 25

    fieldsets = (
        ('Основная информация', {
            'fields': (
                'user',
                'mistake_type',
                'task',
                'fine',
            )
        }),
        ('Дополнительно', {
            'fields': (
                'tip',
                'is_tip_shown',
            ),
            'classes': ('collapse',)
        }),
    )

    def get_user_id(self, obj):
        return obj.user.user_id
    get_user_id.short_description = 'ID пользователя'
    get_user_id.admin_order_field = 'user__user_id'

    def get_task_name(self, obj):
        return obj.task.task_name if obj.task else '-'
    get_task_name.short_description = 'Задание'
    get_task_name.admin_order_field = 'task__task_name'

    def get_mistake_type_display(self, obj):
        return dict(MISTAKE_TYPE_CHOICES.choices).get(obj.mistake_type, '-')
    get_mistake_type_display.short_description = 'Тип ошибки'
    get_mistake_type_display.admin_order_field = 'mistake_type'

    def skills_list(self, obj):
        return ", ".join([skill.name for skill in obj.skills.all()])
    skills_list.short_description = 'Навыки'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'task'
        ).prefetch_related('skills')