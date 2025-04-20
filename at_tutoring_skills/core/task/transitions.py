from venv import logger

from asgiref.sync import sync_to_async

from at_tutoring_skills.apps.skills.models import SUBJECT_CHOICES, Task
from at_tutoring_skills.apps.skills.models import TaskUser
from at_tutoring_skills.apps.skills.models import User


class TransitionsService:
    def __init__(self):
        pass

    async def check_stage_tasks_completed(self, user: User, task_object: int |SUBJECT_CHOICES) -> bool:
        """
        Асинхронно проверяет, завершены ли все задания указанного типа для пользователя

        Args:
            user: Объект пользователя
            task_object_number: Номер типа задания (1-5)

        Returns:
            bool: True если все задания данного типа завершены и существуют, иначе False
        """
        # Проверяем корректность номера типа задания
        @sync_to_async
        def _check_completion():
            # Проверяем наличие незавершенных заданий
            has_uncompleted = TaskUser.objects.filter(
                user=user, task__task_object=task_object, is_completed=False
            ).exists()

            if has_uncompleted:
                return False

            # Проверяем существование заданий данного типа
            return Task.objects.filter(task_object=task_object).exists()

        try:
            return await _check_completion()
        except Exception as e:
            logger.error(f"Error checking task completion: {str(e)}")
            return False
