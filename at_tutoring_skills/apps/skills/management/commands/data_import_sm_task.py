import json
from django.core.management.base import BaseCommand
from at_tutoring_skills.apps.skills.models import Task
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Генерирует и импортирует задачи для модели simulation'

    def handle(self, *args, **options):
        """Основной обработчик команды"""
        try:
            # Генерация JSON-файла с задачами
            filename = self.generate_tasks_json()

            # Импорт задач из JSON-файла в базу данных
            stats = self.import_tasks_from_json(filename)

            # Вывод результатов
            self.stdout.write(
                self.style.SUCCESS(
                    f"Успешно создано {stats['created']} задач. "
                    f"Обновлено: {stats['updated']}. Ошибок: {stats['errors']}."
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {str(e)}"))

    def generate_tasks_json(self, filename: str = "generated_tasks_sm.json") -> str:
        """
        Генерирует JSON-файл с задачами для модели simulation
        
        Args:
            filename: Имя файла для сохранения
            
        Returns:
            str: Путь к сохраненному файлу
        """
        # Определение object_reference для типа ресурса "Пострадавший"
        object_reference = {
            "id": 6,
            "name": "Потерпевший",
            "type": "CONSTANT",
            "attributes": [
                {
                    "id": 1,
                    "name": "Приоритет_пострадавшего",
                    "type": "INT",
                    "default_value": 1
                },
                {
                    "id": 2,
                    "name": "Состояние",
                    "type": "INT",
                    "default_value": 1
                },
                {
                    "id": 3,
                    "name": "Степень_тяжести",
                    "type": "ENUM",
                    "enum_values_set": ["Легкая", "Средняя", "Тяжелая", "Очень_тяжелая"],
                    "default_value": "Легкая"
                }
            ]
        }

        # Создание задачи
        tasks_template = [
            {
                "task_name": "Создать тип ресурса 'Потерпевший'",
                "task_object": 6,  # Например, тип объекта (ресурс)
                "object_name": "Потерпевший",
                "description": "Задача по созданию типа ресурса 'Потерпевший' для модели simulation",
                "object_reference": object_reference
            }
        ]

        # Сохранение в JSON-файл
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(tasks_template, f, indent=4, ensure_ascii=False)  # Убедитесь, что ensure_ascii=False

        return filename

    def import_tasks_from_json(self, filename: str = "generated_tasks_sm.json") -> dict:
        """
        Импортирует задачи из JSON-файла в базу данных
        
        Args:
            filename: Путь к JSON-файлу
            
        Returns:
            dict: Статистика импорта {
                'total': int,
                'created': int,
                'updated': int,
                'errors': int
            }
        """
        stats = {'total': 0, 'created': 0, 'updated': 0, 'errors': 0}

        try:
            # Чтение JSON-файла
            with open(filename, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)

            stats['total'] = len(tasks_data)

            for item in tasks_data:
                try:
                    with transaction.atomic():
                        # Преобразование данных для модели Task
                        task_data = {
                            "task_name": item['task_name'],
                            "task_object": item['task_object'],
                            "object_name": item['object_name'],
                            "description": item['description'],
                            "object_reference": json.dumps(item['object_reference'], ensure_ascii=False)  # Преобразуем в JSON-строку
                        }

                        # Создание или обновление задачи
                        task, created = Task.objects.update_or_create(
                            object_name=item['object_name'],
                            defaults=task_data
                        )

                        if created:
                            stats['created'] += 1
                            logger.info(f"Создана задача: {task.object_name}")
                        else:
                            stats['updated'] += 1
                            logger.debug(f"Обновлена задача: {task.object_name}")

                except Exception as e:
                    stats['errors'] += 1
                    logger.error(f"Ошибка обработки задачи {item.get('object_name', 'unknown')}: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Ошибка чтения файла: {str(e)}")
            stats['errors'] += 1

        return stats

    def display_tasks(self):
        """
        Выводит все задачи из базы данных в читаемом формате
        """
        for task in Task.objects.all():
            try:
                # Преобразуем JSON-строку обратно в словарь
                object_reference = json.loads(task.object_reference)
            except (json.JSONDecodeError, TypeError):
                object_reference = task.object_reference  # Если данные уже словарь

            print(f"ID: {task.id}, Name: {task.task_name}, Object Reference: {object_reference}")