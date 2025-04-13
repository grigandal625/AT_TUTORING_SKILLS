# import json
import json
import logging

from asgiref.sync import sync_to_async
from at_krl.models.kb_class import KBClassModel
from at_krl.models.kb_rule import KBRuleModel
from at_krl.models.kb_type import KBFuzzyTypeModel
from at_krl.models.kb_type import KBNumericTypeModel
from at_krl.models.kb_type import KBSymbolicTypeModel
from at_krl.models.temporal.allen_event import KBEventModel
from at_krl.models.temporal.allen_interval import KBIntervalModel
from at_krl.utils.context import Context as ATKRLContext
from django.db import DatabaseError
from django.db import models
from django.db import transaction
from pydantic import RootModel

from at_tutoring_skills.apps.mistakes.models import Mistake
from at_tutoring_skills.apps.mistakes.models import MISTAKE_TYPE_CHOICES
from at_tutoring_skills.apps.skills.models import Skill
from at_tutoring_skills.apps.skills.models import Task
from at_tutoring_skills.apps.skills.models import TaskUser
from at_tutoring_skills.apps.skills.models import User
from at_tutoring_skills.apps.skills.models import UserSkill
from at_tutoring_skills.core.errors.models import CommonMistake
from at_tutoring_skills.core.service.simulation.subservice.function.models.models import FunctionParameterRequest
from at_tutoring_skills.core.service.simulation.subservice.function.models.models import FunctionRequest
from at_tutoring_skills.core.service.simulation.subservice.resource.models.models import ResourceAttributeRequest
from at_tutoring_skills.core.service.simulation.subservice.resource.models.models import ResourceRequest
from at_tutoring_skills.core.service.simulation.subservice.resource_type.models.models import (
    ResourceTypeAttributeRequest,
)
from at_tutoring_skills.core.service.simulation.subservice.resource_type.models.models import ResourceTypeRequest

logger = logging.getLogger(__name__)


class KBTypeRootModel(RootModel[KBSymbolicTypeModel | KBNumericTypeModel | KBFuzzyTypeModel]):
    def to_internal(self, context):
        return self.root.to_internal(context=context)


class KBTaskService:
    async def get_type_reference(self, task: Task):
        context = ATKRLContext(name="1")
        d = task.object_reference  # jsom
        kb_type = KBTypeRootModel(**d)
        return kb_type.to_internal(context)

    async def get_object_reference(self, task: Task):
        context = ATKRLContext(name="1")
        d = task.object_reference  # jsom
        kb_object = KBClassModel(**d)
        return kb_object.to_internal(context)

    async def get_event_reference(self, task: Task):
        context = ATKRLContext(name="1")
        d = task.object_reference  # jsom
        kb_event = KBEventModel(**d)
        return kb_event.to_internal(context)

    async def get_interval_reference(self, task: Task):
        context = ATKRLContext(name="1")
        d = task.object_reference  # jsom
        kb_event = KBIntervalModel(**d)
        return kb_event.to_internal(context)

    async def get_rule_reference(self, task: Task):
        context = ATKRLContext(name="1")
        d = task.object_reference  # jsom
        kb_event = KBRuleModel(**d)
        return kb_event.to_internal(context)


# #можешь переименовать
class KBIMServise:
    async def get_resource_type_reference(self, task: Task) -> ResourceTypeRequest:
        # Получаем эталонные данные из task.object_reference
        if isinstance(task.object_reference, str):
            reference_data = json.loads(task.object_reference)

        elif isinstance(task.object_reference, dict):
            reference_data = task.object_reference

        else:
            raise ValueError("task.object_reference должен быть строкой JSON или словарём")

        # Преобразуем данные в объект ResourceTypeRequest
        attributes = [ResourceTypeAttributeRequest(**attr_data) for attr_data in reference_data["attributes"]]

        return ResourceTypeRequest(
            id=reference_data["id"], name=reference_data["name"], type=reference_data["type"], attributes=attributes
        )

    async def get_resource_reference(self, task: Task):
        if isinstance(task.object_reference, str):
            reference_data = json.loads(task.object_reference)

        elif isinstance(task.object_reference, dict):
            reference_data = task.object_reference

        else:
            raise ValueError("task.object_reference должен быть строкой JSON или словарём")

        attributes = [ResourceAttributeRequest(**attr_data) for attr_data in reference_data["attributes"]]

        return ResourceRequest(
            id=reference_data["id"], name=reference_data["name"], type=reference_data["type"], attributes=attributes
        )

    async def get_template_reference(self, task: Task):
        ...

    async def get_template_usage_reference(self, task: Task):
        ...

    async def get_function_reference(self, task: Task):
        if isinstance(task.object_reference, str):
            reference_data = json.loads(task.object_reference)

        elif isinstance(task.object_reference, dict):
            reference_data = task.object_reference

        else:
            raise ValueError("task.object_reference должен быть строкой JSON или словарём")

        attributes = [FunctionParameterRequest(**attr_data) for attr_data in reference_data["attributes"]]

        return FunctionRequest(
            id=reference_data["id"], name=reference_data["name"], type=reference_data["type"], attributes=attributes
        )


class TaskService(KBTaskService, KBIMServise):
    kb_service: KBTaskService

    def __init__(self):
        # self.repository = repository
        self.kb_service = KBTaskService()

    async def increment_taskuser_attempts(self, task: Task, user: User) -> bool:
        """
        Увеличивает счетчик попыток только для существующих записей (Django <5.0)
        """

        @sync_to_async
        def _increment_attempts():
            return TaskUser.objects.filter(task=task, user=user).update(attempts=models.F("attempts") + 1)

        try:
            updated = await _increment_attempts()
            return updated > 0
        except Exception as e:
            print(f"Ошибка: {str(e)}")
            return False

    async def complete_task(self, task: Task, user: User):
        """
        Помечает задание как выполненное (Django <5.0)
        Только обновляет существующую запись, не создает новую
        """

        @sync_to_async
        def _complete_task():
            try:
                with transaction.atomic():
                    task_user = TaskUser.objects.select_for_update().get(task=task, user=user)
                    task_user.is_completed = True
                    task_user.attempts = models.F("attempts") + 1
                    task_user.save()
                    return task_user
            except TaskUser.DoesNotExist:
                return None

        try:
            task_user = await _complete_task()
            if task_user and task_user.is_completed:
                await self.increment_taskuser_attempts(task, user)
            return task_user is not None
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

    async def append_mistake(self, mistake: CommonMistake) -> bool:
        """
        Асинхронно сохраняет ошибку в базу с использованием async-ORM Django

        Args:
            mistake: Объект ошибки CommonMistake

        Returns:
            bool: True при успешном сохранении, False при ошибке
        """
        try:
            # Для Django < 4.2 используем sync_to_async для транзакции
            from asgiref.sync import sync_to_async

            @sync_to_async
            def _create_mistake():
                with transaction.atomic():
                    user = User.objects.filter(user_id=mistake.user_id).first()
                    if not user:
                        logger.warning(f"User {mistake.user_id} not found")
                        return False

                    task = Task.objects.filter(pk=mistake.task_id).first() if mistake.task_id else None
                    skills = Skill.objects.filter(code__in=mistake.skills) if mistake.skills else None

                    mistake_data = {
                        "user": user,
                        "task": task,
                        "fine": mistake.fine * mistake.coefficient,
                        "tip": mistake.tip,
                        "is_tip_shown": False,
                    }

                    if mistake.type == "syntax":
                        new_mistake = Mistake.objects.create(mistake_type=MISTAKE_TYPE_CHOICES.SYNTAX, **mistake_data)
                    elif mistake.type == "logic":
                        new_mistake = Mistake.objects.create(mistake_type=MISTAKE_TYPE_CHOICES.LOGIC, **mistake_data)
                    elif mistake.type == "lexic":
                        new_mistake = Mistake.objects.create(mistake_type=MISTAKE_TYPE_CHOICES.LEXIC, **mistake_data)
                    else:
                        logger.warning(f"Unknown mistake type: {mistake.type}")
                        return False

                    if skills:
                        new_mistake.skills.set(skills)

                    return True

            return await _create_mistake()

        except DatabaseError as e:
            logger.error(f"Database error: {str(e)}")
            return False
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
            logger.warning(f"Task not found: name='{name}'" + (f", type={task_object}" if task_object else ""))
            return None

        except Task.MultipleObjectsReturned:
            tasks = await Task.objects.filter(object_name=name).alist()
            logger.error(
                f"Multiple tasks found: name='{name}'"
                + (f", type={task_object}" if task_object else "")
                + f". Returning first of {len(tasks)}"
            )
            return tasks[0]

    async def create_user_skill_connection(self, user: User) -> tuple[int, int]:
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
                obj, created = UserSkill.objects.get_or_create(user=user, skill=skill, defaults={"is_completed": False})
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

    def populate_task_skills(self, tasks: list[Task], skills: list[Skill]) -> dict:
        """
        Создает связи ManyToMany между задачами и навыками (синхронная версия)
        с использованием pk вместо id

        Args:
            tasks: Список объектов Task
            skills: Список объектов Skill

        Returns:
            dict: Статистика выполнения
        """
        stats = {"total_pairs": len(tasks) * len(skills), "created": 0, "existing": 0, "errors": 0}

        try:
            with transaction.atomic():
                for task in tasks:
                    for skill in skills:
                        try:
                            # Используем pk вместо id
                            _, created = task.skills.through.objects.get_or_create(task_id=task.pk, skill_id=skill.pk)
                            if created:
                                stats["created"] += 1
                            else:
                                stats["existing"] += 1
                        except Exception as e:
                            stats["errors"] += 1
                            logger.error(f"Error linking task {task.pk} with skill {skill.pk}: {str(e)}")
            return stats
        except Exception as e:
            logger.error(f"Critical error: {str(e)}")
            stats["errors"] = stats["total_pairs"]
            return stats

    async def create_task_user_safe(self, task: Task, user: User) -> tuple[TaskUser, bool]:
        """
        Создает запись TaskUser, только если её не существует.
        Если запись уже есть — возвращает её БЕЗ ИЗМЕНЕНИЙ (attempts и is_completed остаются как были).
        Гарантирует, что дубликаты не будут созданы даже в условиях гонки.

        Returns:
            tuple[TaskUser, bool]: (объект TaskUser, created: bool)
        """

        @sync_to_async
        def _create_or_get_task_user():
            try:
                # Сначала пробуем найти существующую запись
                task_user = TaskUser.objects.filter(task=task, user=user).first()
                if task_user:
                    return task_user, False

                # Если записи нет - создаем новую
                with transaction.atomic():
                    # Двойная проверка для защиты от race condition
                    if TaskUser.objects.filter(task=task, user=user).exists():
                        return TaskUser.objects.get(task=task, user=user), False

                    task_user = TaskUser.objects.create(task=task, user=user)
                    return task_user, True
            except Exception as e:
                # В случае любой ошибки пытаемся вернуть существующую запись
                existing = TaskUser.objects.filter(task=task, user=user).first()
                if existing:
                    return existing, False
                raise ValueError(f"Failed to create or get TaskUser: {str(e)}")

        return await _create_or_get_task_user()

    # @sync_to_async
    #     def _create_or_get_task_user():
