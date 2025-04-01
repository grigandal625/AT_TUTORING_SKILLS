from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from at_tutoring_skills.apps.skills.models import TaskUser  # Замените `your_app` на имя вашего приложения

class Command(BaseCommand):
    help = "Очищает таблицу TaskUser (удаляет все записи)."  # Описание команды

    def add_arguments(self, parser):
        # Опциональные аргументы (например, подтверждение удаления)
        parser.add_argument(
            "--noinput",
            action="store_true",
            help="Автоматически подтверждать удаление без запроса.",
        )

    def handle(self, *args, **options):
        noinput = options["noinput"]

        # Получаем количество записей перед удалением
        count = TaskUser.objects.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS("Таблица TaskUser уже пуста."))
            return

        # Запрос подтверждения (если не указан --noinput)
        if not noinput:
            confirm = input(
                f"Вы уверены, что хотите удалить ВСЕ {count} записей из TaskUser? [y/N] "
            )
            if confirm.lower() != "y":
                self.stdout.write("Отменено.")
                return

        # Удаление в транзакции для безопасности
        try:
            with transaction.atomic():
                deleted_count = TaskUser.objects.all().delete()[0]
                self.stdout.write(
                    self.style.SUCCESS(f"Удалено {deleted_count} записей.")
                )
        except Exception as e:
            raise CommandError(f"Ошибка при удалении: {e}")