import json
import logging

from at_krl.core.kb_class import PropertyDefinition
from at_krl.core.kb_rule import KBRule
from at_krl.core.kb_type import KBType
from at_krl.core.knowledge_base import KnowledgeBase
from at_krl.core.temporal.allen_event import KBEvent
from at_krl.core.temporal.allen_interval import KBInterval
from django.core.management.base import BaseCommand

from at_tutoring_skills.apps.skills.models import SUBJECT_CHOICES

logger = logging.getLogger(__name__)

"""
записать содержимое формата kbs в txt и поменять имя файла в file_name
экспорт в корневую папку, файл :generated_tasks.json
"""


class Command(BaseCommand):
    help = "Заполняет базу данных из JSON файлов и KRL текста"

    def handle(self, *args, **options):
        try:
            text = None
            file_name = "TrafficAccidentsKB_test"
            with open(
                f"at_tutoring_skills/apps/skills/management/commands/{file_name}.txt", "r", encoding="utf-8"
            ) as f:
                text = f.read()
            kb = self.get_knowledge_base(text)
            json_file = self.generate_tasks_json(kb)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Критическая ошибка: {str(e)}"))

    def get_knowledge_base(self, text: str) -> list:
        """Парсинг KRL текста"""
        kb = KnowledgeBase.from_krl(text)
        return list(kb.types) + list(kb.world.properties) + list(kb.classes.temporal_objects) + list(kb.rules)

    def generate_tasks_json(self, knowledge_array: list, filename: str = "generated_tasks.json") -> str:
        """Генерация JSON с задачами"""
        tasks = []
        for item in knowledge_array:
            if isinstance(item, KBType):
                task_object = SUBJECT_CHOICES.KB_TYPE.value
                name = "тип"
                repr = item.to_representation()
            elif isinstance(item, (KBEvent)):
                task_object = SUBJECT_CHOICES.KB_EVENT.value
                name = "событие"
                repr = item.to_representation()
            elif isinstance(item, (KBInterval)):
                task_object = SUBJECT_CHOICES.KB_INTERVAL.value
                name = "интервал"
                repr = item.to_representation()
            elif isinstance(item, (KBRule)):
                task_object = SUBJECT_CHOICES.KB_RULE.value
                name = "правило"
                repr = item.to_representation()

            elif isinstance(item, PropertyDefinition):
                task_object = SUBJECT_CHOICES.KB_OBJECT.value
                name = "объект"
                repr = item.type.target.to_representation()
                repr["id"] = item.id

            print(repr)
            tasks.append(
                {
                    "task_name": f"Создать {name} {item.id}",
                    "task_object": task_object,
                    "object_name": item.id,
                    "description": "",
                    "object_reference": repr,
                }
            )

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(tasks, f, indent=4, ensure_ascii=False)
        return filename
