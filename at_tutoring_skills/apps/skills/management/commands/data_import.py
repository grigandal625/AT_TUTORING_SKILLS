import json

from django.core.management.base import BaseCommand

from at_tutoring_skills.apps.skills.models import Skill
from at_tutoring_skills.apps.skills.models import Task


class Command(BaseCommand):
    help = "Загружает данные из JSON в базу данных"

    def handle(self, *args, **kwargs):
        # Загружаем данные для навыков
        with open("import_files/skills.json", "r", encoding="utf-8") as f:
            skills_data = json.load(f)

        for skill_data in skills_data:
            skill, created = Skill.objects.update_or_create(
                id=skill_data["id"],
                defaults={"name": skill_data["name"], "group": skill_data["group"]},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Навык "{skill.name}" успешно создан.'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Навык "{skill.name}" уже существует.'))

        # Загружаем данные для заданий
        with open("import_files/tasks.json", "r", encoding="utf-8") as f:
            tasks_data = json.load(f)

        for task_data in tasks_data:
            task, created = Task.objects.update_or_create(
                defaults={
                    "task_name": task_data["task_name"],
                    "task_object": task_data["task_object"],
                    "object_name": task_data["object_name"],
                    "description": task_data.get("description", ""),
                    "object_reference": task_data["object_reference"],
                },
            )
            # # Привязываем навыки к задаче
            # for skill_id in task_data["skills"]:
            #     try:
            #         skill = Skill.objects.get(id=skill_id)
            #         task.skills.add(skill)
            #     except Skill.DoesNotExist:
            #         self.stdout.write(self.style.ERROR(f"Навык с ID {skill_id} не найден."))

            if created:
                self.stdout.write(self.style.SUCCESS(f'Задание "{task.task_name}" успешно создано.'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Задание "{task.task_name}" уже существует.'))