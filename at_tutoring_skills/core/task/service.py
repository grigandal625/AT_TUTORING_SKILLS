from typing import Protocol
from django.db import models
from at_tutoring_skills.apps.skills.models import SUBJECT_CHOICES, Task, TaskUser, User, UserSkill

import logging
from django.db import transaction

logger = logging.getLogger(__name__)

class Repository(Protocol):
    # Логика добавления ошибка в БД из Django
    ...

class TaskService:
    def __init__(self, repository: Repository):
        self.repository = repository

    async def increment_existing_attempts(self, task: Task, user: User):
        """
        Увеличивает счетчик попыток только для существующих записей
        """
        try:
            updated = await TaskUser.objects.filter(
                task=task,
                user=user
            ).aupdate(attempts=models.F()('attempts') + 1)
            
            return updated > 0  # True если запись была обновлена
                
        except Exception as e:
            print(f"Ошибка: {str(e)}")
            return False

    async def complete_task(self, task: Task, user: User) -> bool:
        """
        Помечает задание как выполненное для указанного пользователя
        
        Args:
            task: Объект задания (Task)
            user: Объект пользователя (User)
            
        Returns:
            bool: True если операция успешна, False если ошибка
        """
        try:
            with transaction.atomic():
                # Обновляем TaskUser
                task_user, created = await TaskUser.objects.aupdate_or_create(
                    task=task,
                    user=user,
                    defaults={
                        'is_completed': True,
                        'attempts': models.F('attempts') + 1,
                    }
                )
                
                # Обновляем связанные навыки, если задание выполнено
                if task_user.is_completed:
                    await self.increment_existing_attempts(task, user)
                
                return True
                
        except Exception as e:
            print(f"Ошибка при выполнении задания: {str(e)}")
            return False
        # Добавить запись в таблицу TaskUser


    async def get_task_with_logging(self, object_name: str, task_object: str):
        try:
            return await Task.objects.aget(object_name=object_name, task_object=task_object)
        except Task.DoesNotExist:
            logger.warning(f"Task not found: {object_name}, {task_object}")
            return None
        except Task.MultipleObjectsReturned:
            logger.error(f"Multiple tasks found: {object_name}, {task_object}")
            return None
        
