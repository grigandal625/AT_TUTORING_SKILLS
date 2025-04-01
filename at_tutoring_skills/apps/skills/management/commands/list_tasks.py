from django.core.management.base import BaseCommand

from at_tutoring_skills.apps.skills.models import Task


class Command(BaseCommand):
    help = "Выводит все данные из таблицы Task"

    def handle(self, *args, **options):
        # Получение всех записей из таблицы Task
        tasks = Task.objects.all()

        if not tasks.exists():
            self.stdout.write(self.style.WARNING("Таблица Task пуста."))
            return

        # Вывод данных
        for task in tasks:
            self.stdout.write(
                self.style.SUCCESS(
                    f"ID: {task.id}, " f"Name: {task.task_name}, " f"Object Reference: {task.object_reference}"
                )
            )
