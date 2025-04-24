import json
import logging

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count

from at_tutoring_skills.apps.skills.models import SUBJECT_CHOICES, SKillConnection, Skill
from at_tutoring_skills.apps.skills.models import Task
from at_tutoring_skills.apps.skills.models import Variant
from pathlib import Path

logger = logging.getLogger(__name__)

commands_dir = Path(__file__).resolve().parent
data_dir = commands_dir / "data_sm"

class Command(BaseCommand):
    help = "Импортирует задачи из JSON-файла в базу данных"

    def handle(self, *args, **options):
        """Основной обработчик команды"""
        
        try:
            self.create_skills()
            # Импорт задач из JSON-файла в базу данных
            stats = self.import_tasks_from_json()
            # Вывод результатов
            self.stdout.write(
                self.style.SUCCESS(
                    f"Успешно создано {stats['created']} задач. "
                    f"Обновлено: {stats['updated']}. Ошибок: {stats['errors']}."
                )
            )
            self.create_connections_skills(filename=data_dir / "sm_skills_connections.json")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {str(e)}"))

    def import_tasks_from_json(self) -> dict:
        """
        Импортирует задачи из JSON-файлов в базу данных
        Returns:
            dict: Статистика импорта {
                'total': int,
                'created': int,
                'updated': int,
                'errors': int
            }
        """
        stats = {"total": 0, "created": 0, "updated": 0, "errors": 0}
        skills_map = {skill.code: skill for skill in Skill.objects.all()}

        # Загрузка заданий из файлов generated_tasks_*.json
        tasks_files = data_dir.glob("sm_tasks_*.json")

        for tasks_file in tasks_files:
            with open(tasks_file, "r", encoding="utf-8") as f:
                tasks_data = json.load(f)

            variant_name = tasks_data.get("variant_name")
            if not variant_name:
                self.stdout.write(self.style.ERROR(f"Файл {tasks_file.name} не содержит variant_name, пропускаем"))
                stats["errors"] += 1
                continue

            description = tasks_data.get("description", "")

            # Создаем/получаем вариант
            variant, created = Variant.objects.get_or_create(
                name=variant_name, defaults={"kb_description": description}
            )
            variant.kb_description = description
            variant.save()
            action = "Создан" if created else "Обновлен"
            self.stdout.write(f"\n{action} вариант: {variant_name}")

            # Загрузка заданий
            for task_data in tasks_data.get("tasks", []):
                try:
                    with transaction.atomic():
                        # Определение типа задачи
                        task_object = task_data.get("task_object")
                        if task_object == SUBJECT_CHOICES.SIMULATION_RESOURCE_TYPES:
                            task_name = "тип ресурса"
                        elif task_object == SUBJECT_CHOICES.SIMULATION_RESOURCES:
                            task_name = "ресурс"
                        elif task_object == SUBJECT_CHOICES.SIMULATION_TEMPLATES:
                            task_name = "образец операции"
                        elif task_object == SUBJECT_CHOICES.SIMULATION_TEMPLATE_USAGES:
                            task_name = "операцию"
                        elif task_object == SUBJECT_CHOICES.SIMULATION_FUNCS:
                            task_name = "функцию"
                        else:
                            task_name = "Неизвестный тип"

                        # Подготовка данных задачи
                        prepared_task_data = {
                            "task_name": f'Создать {task_name} "{task_data.get("object_name")}"',
                            "task_object": task_data.get("task_object"),
                            "object_name": task_data.get("object_name"),
                            "description": task_data.get("description"),
                            "object_reference": task_data.get("object_reference", {}),
                        }

                        # Создание или обновление задачи
                        task, created = Task.objects.update_or_create(
                            object_name=task_data["object_name"],
                            defaults=prepared_task_data
                        )

                        # Связывание с вариантом
                        variant.task.add(task)

                        # Связывание с навыками
                        skill_codes = task_data.get("skill_codes", [])
                        for code in skill_codes:
                            if code in skills_map:
                                task.skills.add(skills_map[code])
                                self.stdout.write(f"  Связано с навыком: {skills_map[code].name}")
                            else:
                                self.stdout.write(
                                    self.style.WARNING(f"  Навык с кодом {code} не найден для задания {task.task_name}")
                                )
                                stats["errors"] += 1

                        action = "Создано" if created else "Обновлено"
                        self.stdout.write(f"  {action} задание: {task.task_name}")

                        if created:
                            stats["created"] += 1
                        else:
                            stats["updated"] += 1
                        stats["total"] += 1

                except Exception as e:
                    stats["errors"] += 1
                    logger.error(f"Ошибка обработки задачи {task_data.get('object_name', 'unknown')}: {str(e)}")
                    continue

        return stats

    def remove_duplicate_tasks(self):
        """
        Удаляет дубликаты задач на основе поля object_name.
        Оставляет только одну задачу для каждого уникального значения object_name.
        """
        try:
            # Найти все дубликаты
            duplicates = Task.objects.values("object_name").annotate(count=Count("id")).filter(count__gt=1)

            for duplicate in duplicates:
                object_name = duplicate["object_name"]
                tasks = Task.objects.filter(object_name=object_name)
                # Оставить только одну задачу, остальные удалить
                for task in tasks[1:]:
                    task.delete()
                    logger.info(f"Удален дубликат задачи: {object_name}")

            logger.info("Проверка и удаление дубликатов завершено.")

        except Exception as e:
            logger.error(f"Ошибка при удалении дубликатов задач: {str(e)}")

    def display_tasks(self):
        """
        Выводит все задачи из базы данных в читаемом формате
        """
        for task in Task.objects.all():
            try:
                # Преобразуем JSON-строку обратно в словарь
                object_reference = task.object_reference
            except (json.JSONDecodeError, TypeError):
                object_reference = task.object_reference  # Если данные уже словарь
            print(f"ID: {task.id}, Name: {task.task_name}, Object Reference: {object_reference}")

    def create_skills(self, skills_file: str = data_dir / "sm_skills.json"):
        skills_map = {}  # Для хранения соответствия code -> skill

        if skills_file.exists():
            with open(skills_file, "r", encoding="utf-8") as f:
                skills_data = json.load(f)

            for skill_data in skills_data.get("skills", []):
                skill, created = Skill.objects.get_or_create(
                    code=skill_data["code"], 
                    defaults={"name": skill_data["name"], "group": skill_data["group"]}
                )
                skills_map[skill.code] = skill
                action = "Создан" if created else "Обновлен"
                self.stdout.write(f"{action} навык: {skill.name} (код: {skill.code})")

    def create_connections_skills(self, filename: str = data_dir / "sm_skills_connections.json"):
        """Создает или обновляет связи между навыками из JSON-файла"""
        if not filename.exists():
            self.stdout.write(self.style.ERROR(f"Файл {filename} не найден"))
            return

        # Создаем mapping code -> skill для быстрого доступа
        skills_map = {skill.code: skill for skill in Skill.objects.all()}
        
        self.stdout.write("\nЗагрузка связей между навыками...")
        
        created_count = 0
        updated_count = 0
        error_count = 0

        with transaction.atomic():
            with open(filename, "r", encoding="utf-8") as f:
                connections_data = json.load(f)

            for connection_item in connections_data:
                skill_to_code = connection_item["skill"]
                skill_to = skills_map.get(skill_to_code)

                if not skill_to:
                    self.stdout.write(
                        self.style.WARNING(f"  Навык с кодом {skill_to_code} не найден (пропускаем связи)"))
                    error_count += 1
                    continue

                for skill_from_code, weight in zip(connection_item["in_skill"], connection_item["weights"]):
                    skill_from = skills_map.get(skill_from_code)

                    if not skill_from:
                        self.stdout.write(
                            self.style.WARNING(f"  Навык с кодом {skill_from_code} не найден (связь с {skill_to_code})"))
                        error_count += 1
                        continue

                    try:
                        # Создаем или обновляем связь
                        connection, created = SKillConnection.objects.update_or_create(
                            skill_from=skill_from,
                            skill_to=skill_to,
                            defaults={'weight': weight}
                        )

                        if created:
                            created_count += 1
                            self.stdout.write(
                                f"  Создана связь: {skill_from_code} -> {skill_to_code} (вес: {weight})")
                        else:
                            updated_count += 1
                            self.stdout.write(
                                f"  Обновлена связь: {skill_from_code} -> {skill_to_code} (новый вес: {weight})")

                    except Exception as e:
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(f"  Ошибка создания связи {skill_from_code}->{skill_to_code}: {str(e)}"))

        # Итоговая статистика
        self.stdout.write("\nИтоги загрузки связей:")
        self.stdout.write(f"  Успешно создано: {created_count}")
        self.stdout.write(f"  Обновлено: {updated_count}")
        self.stdout.write(f"  Ошибок: {error_count}")
        self.stdout.write(self.style.SUCCESS("Загрузка связей завершена!"))