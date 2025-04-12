from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import transaction

from at_tutoring_skills.apps.skills.models import (
    Skill, 
    Task, 
    Variant, 
    User, 
    TaskUser, 
    UserSkill
)


class Command(BaseCommand):
    help = "Очищает всю базу данных приложения skills (удаляет все записи всех моделей)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--noinput",
            action="store_true",
            help="Автоматически подтверждать удаление без запроса.",
        )

    def handle(self, *args, **options):
        noinput = options["noinput"]
        
        # Получаем количество записей для всех моделей
        models_counts = {
            'Skill': Skill.objects.count(),
            'Task': Task.objects.count(),
            'Variant': Variant.objects.count(),
            'User': User.objects.count(),
            'TaskUser': TaskUser.objects.count(),
            'UserSkill': UserSkill.objects.count(),
        }
        
        total_count = sum(models_counts.values())
        
        if total_count == 0:
            self.stdout.write(self.style.SUCCESS("Все таблицы уже пусты."))
            return

        # Выводим статистику по таблицам
        self.stdout.write("Количество записей для удаления:")
        for model_name, count in models_counts.items():
            self.stdout.write(f"  {model_name}: {count}")
        self.stdout.write(f"Всего записей: {total_count}")

        # Запрос подтверждения (если не указан --noinput)
        if not noinput:
            confirm = input(f"\nВы уверены, что хотите удалить ВСЕ {total_count} записей? [y/N] ")
            if confirm.lower() != 'y':
                self.stdout.write("Отменено.")
                return

        # Удаление в транзакции для безопасности
        try:
            with transaction.atomic():
                # Важно соблюдать порядок удаления из-за внешних ключей
                deleted = {
                    'UserSkill': UserSkill.objects.all().delete()[0],
                    'TaskUser': TaskUser.objects.all().delete()[0],
                    'User': User.objects.all().delete()[0],
                    'Variant': Variant.objects.all().delete()[0],
                    'Task': Task.objects.all().delete()[0],
                    'Skill': Skill.objects.all().delete()[0],
                }
                
                self.stdout.write("\nРезультат удаления:")
                for model_name, count in deleted.items():
                    self.stdout.write(f"  Удалено из {model_name}: {count}")
                
                self.stdout.write(
                    self.style.SUCCESS(f"\nУспешно удалено {sum(deleted.values())} записей из всех таблиц.")
                )
        except Exception as e:
            raise CommandError(f"Ошибка при удалении: {e}")