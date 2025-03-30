# import json
from typing import Protocol
from django.db import models
from at_tutoring_skills.apps.skills.models import SUBJECT_CHOICES, Task, TaskUser, User, UserSkill
from at_krl.models.kb_type import KBNumericTypeModel, KBSymbolicTypeModel, KBFuzzyTypeModel
from at_krl.models.kb_class import KBClassModel

from at_krl.models.temporal.allen_event import KBEventModel
from at_krl.models.temporal.allen_interval import KBIntervalModel
from at_krl.models.kb_rule import KBRuleModel
from at_krl.utils.context import Context as ATKRLContext
from pydantic import RootModel

import logging
from django.db import transaction

logger = logging.getLogger(__name__)

class KBTypeRootModel(RootModel[KBNumericTypeModel | KBNumericTypeModel | KBFuzzyTypeModel]):
    def to_internal(self, context):
        return self.root.to_internal(context=context)
    
        
class KBTaskService: ...
#     async def get_type_reference(task: Task):
#         context = ATKRLContext(name  ="1")
#         d = task.object_reference #jsom
#         kb_type = KBTypeRootModel(**d)
#         return kb_type.to_internal(context)
    
#     async def get_object_reference(task: Task):
#         context = ATKRLContext(name  ="1")
#         d = task.object_reference #jsom
#         kb_object = KBClassModel(**d)
#         return kb_object.to_internal(context)
    
#     async def get_event_reference(task: Task):
#         context = ATKRLContext(name  ="1")
#         d = task.object_reference #jsom
#         kb_event = KBEventModel(**d)
#         return kb_event.to_internal(context)
    
#     async def get_interval_reference(task: Task):
#         context = ATKRLContext(name  ="1")
#         d = task.object_reference #jsom
#         kb_event = KBIntervalModel(**d)
#         return kb_event.to_internal(context)
    
#     async def get_rule_reference(task: Task):
#         context = ATKRLContext(name  ="1")
#         d = task.object_reference #jsom
#         kb_event = KBRuleModel(**d)
#         return kb_event.to_internal(context)
    
# #можешь переименовать
class KBIMServise():
    pass

class Repository(Protocol): ...
#     # Логика добавления ошибка в БД из Django
#     ...

class TaskService(KBTaskService): ...
#     def __init__(self, repository: Repository, kb_task_service: KBTaskService):
#         self.repository = repository
#         self.kb = kb_task_service

#     async def increment_existing_attempts(self, task: Task, user: User):
#         """
#         Увеличивает счетчик попыток только для существующих записей
#         """
#         try:
#             updated = await TaskUser.objects.filter(
#                 task=task,
#                 user=user
#             ).aupdate(attempts=models.F()('attempts') + 1)
            
#             return updated > 0  # True если запись была обновлена
                
#         except Exception as e:
#             print(f"Ошибка: {str(e)}")
#             return False

#     async def complete_task(self, task: Task, user: User) -> bool:
#         """
#         Помечает задание как выполненное для указанного пользователя
        
#         Args:
#             task: Объект задания (Task)
#             user: Объект пользователя (User)
            
#         Returns:
#             bool: True если операция успешна, False если ошибка
#         """
#         try:
#             with transaction.atomic():
#                 # Обновляем TaskUser
#                 task_user, created = await TaskUser.objects.aupdate_or_create(
#                     task=task,
#                     user=user,
#                     defaults={
#                         'is_completed': True,
#                         'attempts': models.F('attempts') + 1,
#                     }
#                 )
                
#                 # Обновляем связанные навыки, если задание выполнено
#                 if task_user.is_completed:
#                     await self.increment_existing_attempts(task, user)
                
#                 return True
                
#         except Exception as e:
#             print(f"Ошибка при выполнении задания: {str(e)}")
#             return False
#         # Добавить запись в таблицу TaskUser


#     async def get_task_with_logging(self, object_name: str, task_object: str):
#         try:
#             return await Task.objects.aget(object_name=object_name, task_object=task_object)
#         except Task.DoesNotExist:
#             logger.warning(f"Task not found: {object_name}, {task_object}")
#             return None
#         except Task.MultipleObjectsReturned:
#             logger.error(f"Multiple tasks found: {object_name}, {task_object}")
#             return None

    



