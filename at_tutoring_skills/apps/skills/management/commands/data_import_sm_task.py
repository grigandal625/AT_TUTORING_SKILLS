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
            stats = self.import_tasks_from_json(
                data_dir / "generated_tasks_sm.json"
            )
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

    def import_tasks_from_json(
        self,
        filename: str = data_dir / "generated_tasks_sm.json",
    ) -> dict:
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
        stats = {"total": 0, "created": 0, "updated": 0, "errors": 0}
        skills_map = {}  # Для хранения соответствия code -> skill

        try:
            # Загрузка всех навыков из базы данных
            for skill in Skill.objects.all():
                skills_map[skill.code] = skill

            # Удаление дубликатов задач перед импортом
            self.remove_duplicate_tasks()

            # Чтение JSON-файла
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.debug(f"Загруженные данные: {data}")

            # Проверка, что данные являются словарем
            if not isinstance(data, dict):
                logger.error("Данные в файле не являются словарем. Проверьте структуру JSON.")
                stats["errors"] += 1
                return stats

            # Извлечение списка задач и имени варианта
            tasks_data = data.get("tasks", [])
            variant_name = data.get("variant_name")

            if not tasks_data:
                logger.error("В файле отсутствует список задач или он пуст.")
                stats["errors"] += 1
                return stats

            if not variant_name:
                logger.error("В файле отсутствует имя варианта.")
                stats["errors"] += 1
                return stats

            # Создание или получение варианта
            variant, created = Variant.objects.get_or_create(
                name=variant_name, 
                defaults={"kb_description": data.get("description", "")}
            )
            variant.kb_description = data.get("description", "")
            variant.save()
            
            action = "Создан" if created else "Обновлен"
            self.stdout.write(f"\n{action} вариант: {variant_name}")

            stats["total"] = len(tasks_data)

            for item in tasks_data:
                try:
                    with transaction.atomic():
                        # Проверка, что элемент является словарем
                        if not isinstance(item, dict):
                            logger.error(f"Некорректный элемент в данных: {item}")
                            stats["errors"] += 1
                            continue
                        
                        # Определение типа задачи
                        task_object = item.get("task_object")
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
                        task_data = {
                            "task_name": f'Создать {task_name} "{item.get("object_name")}"',
                            "task_object": item.get("task_object"),
                            "object_name": item.get("object_name"),
                            "description": item.get("description"),
                            "object_reference": item.get("object_reference", {}),
                        }

                        # Создание или обновление задачи
                        task, created = Task.objects.update_or_create(
                            object_name=item["object_name"], 
                            defaults=task_data
                        )

                        action = "Создано" if created else "Обновлено"
                        self.stdout.write(f"  {action} задание: {task.task_name}")

                        if created:
                            stats["created"] += 1
                        else:
                            stats["updated"] += 1

                        # Связывание с вариантом
                        variant.task.add(task)

                        # Связывание с навыками
                        skill_codes = item.get("skill_codes", [])
                        for code in skill_codes:
                            if code in skills_map:
                                task.skills.add(skills_map[code])
                                self.stdout.write(f"  Связано с навыком: {skills_map[code].name}")
                            else:
                                self.stdout.write(
                                    self.style.WARNING(f"  Навык с кодом {code} не найден для задания {task.task_name}")
                                )
                                stats["errors"] += 1

                except Exception as e:
                    stats["errors"] += 1
                    logger.error(f"Ошибка обработки задачи {item.get('object_name', 'unknown')}: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Ошибка чтения файла {filename}: {str(e)}")
            stats["errors"] += 1

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
        if not filename.exists():
            self.stdout.write(self.style.ERROR(f"File {filename} not found"))
            return

        with transaction.atomic():
            # Load connections data
            with open(filename, "r", encoding="utf-8") as f:
                connections_data = json.load(f)

            # Create a mapping of skill codes to Skill objects for faster lookup
            skills_map = {skill.code: skill for skill in Skill.objects.all()}

            created_count = 0
            updated_count = 0
            
            self.stdout.write("\nЗагрузка связей между навыками...")

            for item in connections_data:
                skill_to_code = item['skill']
                skill_to = skills_map.get(skill_to_code)
                
                if not skill_to:
                    self.stdout.write(
                        self.style.WARNING(f'  Навык с кодом {skill_to_code} не найден (пропускаем связи)')
                    )
                    continue

                for skill_from_code, weight in zip(item['in_skill'], item['weights']):
                    skill_from = skills_map.get(skill_from_code)
                    
                    if not skill_from:
                        self.stdout.write(
                            self.style.WARNING(f'  Навык с кодом {skill_from_code} не найден (связь с {skill_to_code})')
                        )
                        continue

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

            self.stdout.write(f"  Создано {created_count} новых связей")
            self.stdout.write(f"  Обновлено {updated_count} существующих связей")
            self.stdout.write(self.style.SUCCESS("Загрузка связей между навыками завершена!"))