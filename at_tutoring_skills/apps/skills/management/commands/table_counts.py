from django.core.management.base import BaseCommand
from at_tutoring_skills.apps.skills.models import (
    Skill,
    Task,
    Variant,
    User,
    TaskUser,
    UserSkill
)

class Command(BaseCommand):
    help = 'Показывает количество записей во всех таблицах приложения skills'

    def handle(self, *args, **options):
        # Словарь с моделями и их читаемыми названиями
        models = {
            'Skill': Skill,
            'Task': Task,
            'Variant': Variant,
            'User': User,
            'TaskUser': TaskUser,
            'UserSkill': UserSkill
        }
        
        self.stdout.write("Статистика записей в таблицах:")
        self.stdout.write("-" * 40)
        
        for name, model in models.items():
            try:
                count = model.objects.count()
                self.stdout.write(
                    f"{name.ljust(10)}: {count} записей "
                    f"(таблица: {model._meta.db_table})"
                )
            except Exception as e:
                self.stdout.write(
                    f"Ошибка при подсчёте {name}: {str(e)}"
                )