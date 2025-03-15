# import json

# from django.core.management.base import BaseCommand

# from at_tutoring_skills.apps.skills.models import Event
# from at_tutoring_skills.apps.skills.models import Reaction
# from at_tutoring_skills.apps.skills.models import ScenarioPart
# from at_tutoring_skills.apps.skills.models import Skill
# from at_tutoring_skills.apps.skills.models import Task


# class Command(BaseCommand):
#     help = "Загружает данные из JSON в базу данных"

#     def handle(self, *args, **kwargs):
#         # Загружаем данные для навыков
#         with open("import_files/skills.json", "r", encoding="utf-8") as f:
#             skills_data = json.load(f)

#         for skill_data in skills_data:
#             skill, created = Skill.objects.update_or_create(
#                 id=skill_data["id"],
#                 defaults={"name": skill_data["name"], "scenario_name": skill_data.get("scenario_name", "")},
#             )
#             if created:
#                 self.stdout.write(self.style.SUCCESS(f'Навык "{skill.name}" успешно создан.'))
#             else:
#                 self.stdout.write(self.style.SUCCESS(f'Навык "{skill.name}" уже существует.'))

#         # Загружаем данные для заданий
#         with open("import_files/tasks.json", "r", encoding="utf-8") as f:
#             tasks_data = json.load(f)

#         for task_data in tasks_data:
#             task, created = Task.objects.update_or_create(
#                 id=task_data["id"],
#                 defaults={
#                     "task_name": task_data["task_name"],
#                     "description": task_data["description"],
#                     "event_params": task_data.get("event_params", {}),
#                     "on_success": task_data["on_success"],
#                     "on_failure": task_data["on_failure"],
#                 },
#             )

#             # Привязываем навыки к задаче
#             for skill_id in task_data["skills"]:
#                 try:
#                     skill = Skill.objects.get(id=skill_id)
#                     task.skills.add(skill)
#                 except Skill.DoesNotExist:
#                     self.stdout.write(self.style.ERROR(f"Навык с ID {skill_id} не найден."))

#             if created:
#                 self.stdout.write(self.style.SUCCESS(f'Задание "{task.task_name}" успешно создано.'))
#             else:
#                 self.stdout.write(self.style.SUCCESS(f'Задание "{task.task_name}" уже существует.'))

#         # Загружаем данные для реакций
#         with open("reactions.json", "r", encoding="utf-8") as f:
#             reactions_data = json.load(f)

#         for reaction_data in reactions_data:
#             reaction, created = Reaction.objects.update_or_create(
#                 id=reaction_data["id"],
#                 defaults={
#                     "task": Task.objects.get(id=reaction_data["task_id"]),  # Ссылаемся на Task
#                     "message": reaction_data["message"],
#                 },
#             )
#             if created:
#                 self.stdout.write(self.style.SUCCESS(f"Реакция успешно создана для задания с ID {reaction.task.id}."))
#             else:
#                 self.stdout.write(self.style.SUCCESS(f"Реакция для задания с ID {reaction.task.id} уже существует."))

#         # Загружаем данные для частей сценариев
#         with open("import_files/scenario_parts.json", "r", encoding="utf-8") as f:
#             scenario_parts_data = json.load(f)

#         for scenario_part_data in scenario_parts_data:
#             scenario_part, created = ScenarioPart.objects.update_or_create(
#                 id=scenario_part_data["id"],
#                 defaults={
#                     "scenario_name": scenario_part_data["scenario_name"],
#                     "task": Task.objects.get(id=scenario_part_data["task_id"]),
#                     "status": scenario_part_data["status"],
#                 },
#             )

#             # Привязываем родительские задачи
#             for parent_task_id in scenario_part_data["parent_task_ids"]:
#                 try:
#                     parent_task = Task.objects.get(id=parent_task_id)
#                     scenario_part.parent_tasks.add(parent_task)
#                 except Task.DoesNotExist:
#                     self.stdout.write(self.style.ERROR(f"Задача с ID {parent_task_id} не найдена."))

#             if created:
#                 self.stdout.write(
#                     self.style.SUCCESS(f'Часть сценария для "{scenario_part.scenario_name}" успешно создана.')
#                 )
#             else:
#                 self.stdout.write(
#                     self.style.SUCCESS(f'Часть сценария для "{scenario_part.scenario_name}" уже существует.')
#                 )

#         # Загружаем данные для событий
#         with open("import_files/events.json", "r", encoding="utf-8") as f:
#             events_data = json.load(f)

#         for event_data in events_data:
#             event, created = Event.objects.update_or_create(
#                 id=event_data["id"],
#                 defaults={
#                     "operation_type": event_data["operation_type"],
#                     "operand": event_data["operand"],
#                     "params": event_data["params"],
#                     "status": event_data["status"],
#                     "error_code": event_data.get("error_code", None),
#                     "error_message": event_data.get("error_message", ""),
#                     "is_scenario": event_data["is_scenario"],
#                 },
#             )
#             if created:
#                 self.stdout.write(self.style.SUCCESS(f'Событие с операцией "{event.operation_type}" успешно создано.'))
#             else:
#                 self.stdout.write(self.style.SUCCESS(f'Событие с операцией "{event.operation_type}" уже существует.'))
