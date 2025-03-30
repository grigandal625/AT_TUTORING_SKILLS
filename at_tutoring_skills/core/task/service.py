import json
from typing import Protocol
from django.db import models
from at_tutoring_skills.apps.mistakes.models import Mistake
from at_tutoring_skills.apps.skills.models import SUBJECT_CHOICES, Skill, Task, TaskUser, User, UserSkill, Variant
from at_krl.models.kb_type import KBNumericTypeModel, KBSymbolicTypeModel, KBFuzzyTypeModel
from at_krl.models.kb_class import KBClassModel

from at_krl.models.temporal.allen_event import KBEventModel
from at_krl.models.temporal.allen_interval import KBIntervalModel
from at_krl.models.kb_rule import KBRuleModel
from at_krl.utils.context import Context as ATKRLContext
from pydantic import RootModel

from asgiref.sync import sync_to_async

import logging
from django.db import transaction

from at_tutoring_skills.core.errors.models import CommonMistake

logger = logging.getLogger(__name__)

class KBTypeRootModel(RootModel[KBNumericTypeModel | KBNumericTypeModel | KBFuzzyTypeModel]):
    def to_internal(self, context):
        return self.root.to_internal(context=context)
    
        
class KBTaskService:
    async def get_type_reference(self, task: Task):
        context = ATKRLContext(name  ="1")
        d = task.object_reference #jsom
        kb_type = KBTypeRootModel(**d)
        return kb_type.to_internal(context)
    
    async def get_object_reference(self,task: Task):
        context = ATKRLContext(name  ="1")
        d = task.object_reference #jsom
        kb_object = KBClassModel(**d)
        return kb_object.to_internal(context)
    
    async def get_event_reference(self,task: Task):
        context = ATKRLContext(name  ="1")
        d = task.object_reference #jsom
        kb_event = KBEventModel(**d)
        return kb_event.to_internal(context)
    
    async def get_interval_reference(self,task: Task):
        context = ATKRLContext(name  ="1")
        d = task.object_reference #jsom
        kb_event = KBIntervalModel(**d)
        return kb_event.to_internal(context)
    
    async def get_rule_reference(self,task: Task):
        context = ATKRLContext(name  ="1")
        d = task.object_reference #jsom
        kb_event = KBRuleModel(**d)
        return kb_event.to_internal(context)
    
#можешь переименовать
class KBIMServise():
    pass

class Repository(Protocol):
    # Логика добавления ошибка в БД из Django
    ...

class TaskService(KBTaskService):

    kb_service : KBTaskService 
    
    def __init__(self):
        # self.repository = repository
        self.kb_service = KBTaskService()

    async def increment_existing_attempts(self, task: Task, user: User) -> bool:
        """
        Увеличивает счетчик попыток только для существующих записей (Django <5.0)
        """
        @sync_to_async
        def _increment_attempts():
            return TaskUser.objects.filter(
                task=task,
                user=user
            ).update(attempts=models.F('attempts') + 1)

        try:
            updated = await _increment_attempts()
            return updated > 0
        except Exception as e:
            print(f"Ошибка: {str(e)}")
            return False

    async def complete_task(self, task: Task, user: User) -> bool:
        """
        Помечает задание как выполненное (Django <5.0)
        """
        @sync_to_async
        def _complete_task():
            with transaction.atomic():
                task_user, created = TaskUser.objects.update_or_create(
                    task=task,
                    user=user,
                    defaults={
                        'is_completed': True,
                        'attempts': models.F('attempts') + 1,
                    }
                )
                return task_user

        try:
            task_user = await _complete_task()
            if task_user.is_completed:
                await self.increment_existing_attempts(task, user)
            return True
        except Exception as e:
            print(f"Ошибка при выполнении задания: {str(e)}")
            return False

    async def get_task_with_logging(self, object_name: str, task_object: str):
        try:
            return await Task.objects.aget(object_name=object_name, task_object=task_object)
        except Task.DoesNotExist:
            logger.warning(f"Task not found: {object_name}, {task_object}")
            return None
        except Task.MultipleObjectsReturned:
            logger.error(f"Multiple tasks found: {object_name}, {task_object}")
            return None


    @sync_to_async
    def append_mistake(mistake: CommonMistake) -> bool:
        """
        Сохраняет ошибку в базу (асинхронная обёртка для Django <5.0)
        
        Args:
            mistake: Объект ошибки CommonMistake
            
        Returns:
            bool: True при успешном сохранении, False при ошибке
        """
        try:
            with transaction.atomic():
                user = User.objects.filter(user_id=mistake.user_id).first()
                task = Task.objects.filter(pk=mistake.task_id).first()
                
                if not user:
                    logger.warning(f"User {mistake.user_id} not found")
                    return False
                    
                Mistake.objects.create(
                    user=user,
                    mistake_type=mistake.entity_type,
                    task=task,
                    fine=mistake.fine * mistake.coefficient,
                    tip=mistake.tip,
                    is_tip_shown=False
                )
                return True
                
        except Exception as e:
            logger.error(f"Mistake save failed: {str(e)}")
            return False
        
        
    async def create_user(self, auth_token: str) -> tuple[User, bool]:
        """
        Создает нового пользователя или возвращает существующего
        
        Args:
            auth_token: Уникальный идентификатор пользователя
            
        Returns:
            tuple[User, bool]: Кортеж (объект пользователя, флаг создания)
        """
        try:
            # Получаем вариант по умолчанию (если нужен)
            # default_variant = await Variant.objects.filter(name="1").afirst()
            
            # Создаем или получаем пользователя
            user, created = await User.objects.aget_or_create(
                user_id=auth_token,
                # defaults={
                #     'variant': default_variant
                # }
            )
            
            if created:
                logger.info(f"Created new user: {auth_token}")
            else:
                logger.debug(f"User already exists: {auth_token}")
                
            return user, created
            
        except Exception as e:
            logger.error(f"Error creating user {auth_token}: {str(e)}")
            raise  # Можно заменить на возврат None или обработку ошибки

    async def get_task_by_name(self, name: str, task_object: int = None) -> Task | None:
        """
        Получает задание по имени и типу объекта
        
        Args:
            name: Имя задания (object_name)
            task_object: Тип задания из SUBJECT_CHOICES (опционально)
                
        Returns:
            Task: Объект задания или None если не найдено
        """
        try:
            query = Task.objects.filter(object_name=name)
            if task_object is not None:
                query = query.filter(task_object=task_object)
                
            return await query.aget()
            
        except Task.DoesNotExist:
            logger.warning(f"Task not found: name='{name}'" + 
                        (f", type={task_object}" if task_object else ""))
            return None
            
        except Task.MultipleObjectsReturned:
            tasks = await Task.objects.filter(object_name=name).alist()
            logger.error(
                f"Multiple tasks found: name='{name}'" +
                (f", type={task_object}" if task_object else "") +
                f". Returning first of {len(tasks)}"
            )
            return tasks[0]

    async def createUserSkillConnectionAsync(self, user: User) -> tuple[int, int]:
        """
        Асинхронно создает связи UserSkill для всех навыков (совместимость с Django <5.0)
        
        Args:
            user: Объект пользователя
            
        Returns:
            tuple: (created_count, total_skills) - количество созданных связей и общее число навыков
        """
        @sync_to_async
        def _get_all_skills():
            return list(Skill.objects.all())

        @sync_to_async
        def _create_or_update_skill_connection(user, skill):
            
            with transaction.atomic():
                obj, created = UserSkill.objects.get_or_create(
                    user=user,
                    skill=skill,
                    defaults={'is_completed': False}
                )
                return created

        try:
            all_skills = await _get_all_skills()
            created_count = 0
            
            for skill in all_skills:
                created = await _create_or_update_skill_connection(user, skill)
                if created:
                    created_count += 1
            
            return (created_count, len(all_skills))
            
        except Exception as e:
            logger.error(f"Error creating skills for user {user.pk}: {str(e)}")
            return (0, 0)