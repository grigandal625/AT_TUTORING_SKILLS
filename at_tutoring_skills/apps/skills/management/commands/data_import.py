import json
from django.core.management.base import BaseCommand
from at_tutoring_skills.apps.skills.models import Skill, Task, SUBJECT_CHOICES, GROUP_CHOICES
from at_krl.core.knowledge_base import KnowledgeBase
from at_krl.core.kb_type import KBType
from at_krl.core.kb_class import KBClass
from at_krl.core.kb_rule import KBRule
from at_krl.core.temporal.allen_event import KBEvent
from at_krl.core.temporal.allen_interval import KBInterval
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Заполняет базу данных из JSON файлов и KRL текста'
    
    def handle(self, *args, **options):
        # 1. Загрузка навыков
        skills_result = self.load_skills_from_json('C:/Users/Milana/at_marks/AT_TUTORING_SKILLS/at_tutoring_skills/apps/skills/management/commands/kb_skills.json')
        if not skills_result['success']:
            self.stdout.write(self.style.ERROR(f"Ошибка загрузки навыков: {skills_result['error']}"))
            return

        # 2. Генерация и загрузка задач
        try:
            kb = self.get_knowledge_base(self.TEXT)
            json_file = self.generate_tasks_json(kb)
            tasks_result = self.import_tasks_from_json(json_file)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Успешно загружено:\n"
                    f"- Навыков: {skills_result['created']}/{skills_result['total']}\n"
                    f"- Задач: {tasks_result['created']}/{tasks_result['total']}"
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Критическая ошибка: {str(e)}"))

    TEXT = """
    ТИП тип1
    СИМВОЛ
        "Ф"
        "Т"
    КОММЕНТАРИЙ тип1
    ТИП тип2
    ЧИСЛО
        ОТ 0
        ДО 1
    КОММЕНТАРИЙ тип2
    ОБЪЕКТ объект1
    ГРУППА ГРУППА1
        АТРИБУТЫ
        АТРИБУТ атр1
            ТИП тип1
            КОММЕНТАРИЙ атр1
        АТРИБУТ атр2
            ТИП тип2
            КОММЕНТАРИЙ атр2
    КОММЕНТАРИЙ объект1
    """

    def load_skills_from_json(self, file_path: str) -> dict:
        """Загрузка навыков из JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                skills_data = json.load(f)
            
            created = 0
            for skill in skills_data:
                group_value = getattr(GROUP_CHOICES, skill['group']).value
                _, is_created = Skill.objects.get_or_create(
                    name=skill['name'],
                    defaults={'group': group_value}
                )
                if is_created:
                    created += 1
            
            return {'success': True, 'created': created, 'total': len(skills_data), 'error': None}
            
        except Exception as e:
            return {'success': False, 'created': 0, 'total': 0, 'error': str(e)}

    def get_knowledge_base(self, text: str) -> list:
        """Парсинг KRL текста"""
        kb = KnowledgeBase.from_krl(text)  
        return list(kb.types) + list(kb.classes.all) + list(kb.rules)

    def generate_tasks_json(self, knowledge_array: list, filename: str = "generated_tasks.json") -> str:
        """Генерация JSON с задачами"""
        tasks = []
        for item in knowledge_array:
            if isinstance(item, KBType): 
                task_object = SUBJECT_CHOICES.KB_TYPE.value
                name = "тип"
            elif isinstance(item, KBClass):
                task_object = SUBJECT_CHOICES.KB_OBJECT.value
                name = "объект"
            elif isinstance(item, (KBEvent, KBInterval, KBRule)):
                continue  # Для примера обрабатываем только типы и объекты
            
            tasks.append({
                "task_name": f"Создать {name} {item.id}",
                "task_object": task_object,
                "object_name": item.id,
                "description": "",
                "object_reference": item.to_representation()
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=4, ensure_ascii=False)
        return filename

    def import_tasks_from_json(self, filename: str) -> dict:
        """Импорт задач из JSON"""
        stats = {'total': 0, 'created': 0, 'updated': 0, 'errors': 0}
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)
        except Exception as e:
            logger.error(f"Ошибка чтения файла: {str(e)}")
            stats['errors'] = 1
            return stats
        
        stats['total'] = len(tasks_data)
        
        for task_data in tasks_data:
            try:
                with transaction.atomic():
                    task, created = Task.objects.update_or_create(
                        object_name=task_data['object_name'],
                        defaults={
                            'task_name': task_data['task_name'],
                            'task_object': task_data['task_object'],
                            'description': task_data.get('description', ''),
                            'object_reference': task_data.get('object_reference')
                        }
                    )
                    stats['created' if created else 'updated'] += 1
            except Exception as e:
                stats['errors'] += 1
                logger.error(f"Ошибка задачи {task_data.get('object_name')}: {str(e)}")
        
        return stats