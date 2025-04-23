import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from at_tutoring_skills.apps.skills.models import SKillConnection, Skill
from at_tutoring_skills.apps.skills.models import Task
from at_tutoring_skills.apps.skills.models import Variant


class Command(BaseCommand):
    help = "Загружает данные из JSON файлов в базу данных"

    def handle(self, *args, **options):
        commands_dir = Path(__file__).resolve().parent
        data_dir = commands_dir / "data_kb"

        with transaction.atomic():
            # 1. Загрузка всех навыков из единого файла
            skills_file = data_dir / "kb_skills.json"
            skills_map = {}  # Для хранения соответствия code -> skill

            if skills_file.exists():
                with open(skills_file, "r", encoding="utf-8") as f:
                    skills_data = json.load(f)

                for skill_data in skills_data.get("skills", []):
                    skill, created = Skill.objects.get_or_create(
                        code=skill_data["code"], defaults={"name": skill_data["name"], "group": skill_data["group"]}
                    )
                    skills_map[skill.code] = skill
                    action = "Создан" if created else "Обновлен"
                    self.stdout.write(f"{action} навык: {skill.name} (код: {skill.code})")

            # 2. Загрузка заданий из файлов kb_tasks_*.json
            tasks_files = data_dir.glob("kb_tasks_*.json")

            for tasks_file in tasks_files:
                with open(tasks_file, "r", encoding="utf-8") as f:
                    tasks_data = json.load(f)

                variant_name = tasks_data.get("variant_name")
                if not variant_name:
                    self.stdout.write(self.style.ERROR(f"Файл {tasks_file.name} не содержит variant_name, пропускаем"))
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
                    task, created = Task.objects.get_or_create(
                        task_name=task_data["task_name"],
                        defaults={
                            "task_object": task_data["task_object"],
                            "object_name": task_data["object_name"],
                            "description": task_data["description"],
                            "object_reference": task_data.get("object_reference"),
                        },
                    )

                    # Связывание с вариантом
                    variant.task.add(task)

                    # Связывание с навыками
                    for code in task_data.get("skill_codes", []):
                        if code in skills_map:
                            task.skills.add(skills_map[code])
                            self.stdout.write(f"  Связано с навыком: {skills_map[code].name}")
                        else:
                            self.stdout.write(
                                self.style.WARNING(f"  Навык с кодом {code} не найден для задания {task.task_name}")
                            )

                    action = "Создано" if created else "Обновлено"
                    self.stdout.write(f"  {action} задание: {task.task_name}")

            # 3. Загрузка связей между навыками (без удаления существующих)
            connections_file = data_dir / "kb_skills_connections.json"
            if connections_file.exists():
                self.stdout.write("\nЗагрузка связей между навыками...")
                with open(connections_file, "r", encoding="utf-8") as f:
                    connections_data = json.load(f)

                created_count = 0
                updated_count = 0
                for connection_item in connections_data:
                    skill_to_code = connection_item["skill"]
                    skill_to = skills_map.get(skill_to_code)

                    if not skill_to:
                        self.stdout.write(
                            self.style.WARNING(f"  Навык с кодом {skill_to_code} не найден (пропускаем связи)"))
                        continue

                    for skill_from_code, weight in zip(connection_item["in_skill"], connection_item["weights"]):
                        skill_from = skills_map.get(skill_from_code)

                        if not skill_from:
                            self.stdout.write(
                                self.style.WARNING(f"  Навык с кодом {skill_from_code} не найден (связь с {skill_to_code})"))
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

        self.stdout.write(self.style.SUCCESS("\nЗагрузка данных завершена!"))