import json
from django.core.management.base import BaseCommand
from at_tutoring_skills.apps.skills.models import Skill, Task, SUBJECT_CHOICES, GROUP_CHOICES
from django.core.serializers.json import DjangoJSONEncoder
from typing import List
from at_krl.core.knowledge_base import KnowledgeBase
from at_krl.core.kb_type import KBType, KBNumericType, KBSymbolicType, KBFuzzyType
from at_krl.core.kb_class import KBClass
from at_krl.core.kb_rule import KBRule
from at_krl.core.temporal.allen_event import KBEvent
from at_krl.core.temporal.allen_interval import KBInterval
from django.db import transaction
import logging


    
from typing import List, Dict
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Заполняет базу данных из JSON файлов'
    text = """
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

    def handle(self, *args, **options):
        """Основной обработчик команды"""
        json_file = 'skills.json'  # Укажите ваш путь к файлу
        result = self.load_skills_from_json(json_file)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Успешно загружено {result['created']} навыков. "
                    f"Всего записей: {result['total']}"
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(f"Ошибка: {result['error']}")
            )
        kb = self.get_knowledge_base(self.text) 
        self.generate_tasks_json(kb)
        self.import_tasks_from_json()


    def load_skills_from_json(self, file_path: str) -> dict:
        """
        Загружает навыки из JSON-файла в базу данных
        
        Args:
            file_path: Путь к JSON-файлу
            
        Returns:
            dict: Результат операции {
                'success': bool,
                'created': int,
                'total': int,
                'error': str | None
            }
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                skills_data = json.load(f)
            
            created = 0
            for skill in skills_data:
                # Преобразование строки в значение перечисления
                group_value = getattr(GROUP_CHOICES, skill['group']).value
                
                _, is_created = Skill.objects.get_or_create(
                    name=skill['name'],
                    defaults={'group': group_value}
                )
                if is_created:
                    created += 1
            
            return {
                'success': True,
                'created': created,
                'total': len(skills_data),
                'error': None
            }
            
        except FileNotFoundError:
            return {
                'success': False,
                'created': 0,
                'total': 0,
                'error': f"Файл {file_path} не найден"
            }
        except json.JSONDecodeError:
            return {
                'success': False,
                'created': 0,
                'total': 0,
                'error': "Ошибка формата JSON"
            }
        except AttributeError as e:
            return {
                'success': False,
                'created': 0,
                'total': 0,
                'error': f"Неверное значение группы: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'created': 0,
                'total': 0,
                'error': f"Неизвестная ошибка: {str(e)}"
            }

    def load_tasks(self, tasks_data):
        
        for task_data in tasks_data:
            # Преобразуем строковое значение task_object в числовое
            task_object_value = getattr(SUBJECT_CHOICES, task_data['task_object']).value
            
            # Создаем или обновляем задание
            task, created = Task.objects.update_or_create(
                task_name=task_data['task_name'],
                defaults={
                    'task_object': task_object_value,
                    'object_name': task_data.get('object_name', ''),
                    'description': task_data.get('description', ''),
                    'object_reference': task_data.get('object_reference', None)
                }
            )
            
            # Добавляем связанные навыки
            if 'skills' in task_data:
                skills = Skill.objects.filter(name__in=task_data['skills'])
                task.skills.set(skills)

    
    def get_knowledge_base(self, text):
        
        kb =  KnowledgeBase.from_krl(text)  
        array = []
        for type in kb.types:
            array.append(type)
        for object in kb.classes.all:
            array.append(object)
        for rule in kb.rules:
            array.append(rule)

        return array


    def generate_tasks_json(self, object_references: List, filename: str = "generated_tasks.json") -> str:
        """
        Генерирует JSON-файл с задачами на основе массива object_references
        
        Args:
            object_references: Список словарей для поля object_reference
                Пример: [{"type": "A"}, {"type": "B"}]
            filename: Имя файла для сохранения
            
        Returns:
            str: Путь к сохраненному файлу
        """
        tasks_template = []
        
        for idx, obj_ref in enumerate(object_references, start=1):
            if isinstance(obj_ref, KBType): 
                tag = 1
                name  = "тип"
            elif isinstance(obj_ref, KBClass):
                tag = 2
                name  = "объект"
            elif isinstance(obj_ref, KBEvent):
                tag = 3
                name  = "событие"
            elif isinstance(obj_ref, KBInterval):
                tag = 4
                name  = "интервал"
            elif isinstance(obj_ref, KBRule):
                tag =  5
                name  = "правило"

            tasks_template.append({
                "task_name": f"Создать {name} {obj_ref.id}",
                "task_object": tag,  # По умолчанию
                "object_name": obj_ref.id,
                "description": "",
                "object_reference": obj_ref.to_representation() # Основные данные берутся отсюда
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(tasks_template, f, indent=4, ensure_ascii=False)
        
        return filename


    def import_tasks_from_json(self,  filename: str = "generated_tasks.json") -> dict:
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
            with open(filename, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)
        except Exception as e:
            logger.error(f"Ошибка чтения файла: {str(e)}")
            stats['errors'] += 1
            return stats
        
        stats['total'] = len(tasks_data)
        
        for item in tasks_data:
            try:
                with transaction.atomic():
                    task_data = item['fields']
                    
                    task, created =  Task.objects.update_or_create(
                        object_name=task_data['object_name'],
                        defaults={
                            'task_name': task_data['task_name'],
                            'task_object': task_data['task_object'],
                            'description': task_data.get('description', ''),
                            'object_reference': task_data.get('object_reference', None)
                        }
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
        
        return stats




