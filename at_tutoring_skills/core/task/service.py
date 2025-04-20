# import json
import json
import logging
from typing import Union

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
from at_tutoring_skills.apps.skills.models import Task, SUBJECT_CHOICES
from at_tutoring_skills.apps.skills.models import TaskUser
from at_tutoring_skills.apps.skills.models import User
from at_tutoring_skills.apps.skills.models import UserSkill
from at_tutoring_skills.apps.skills.models import Variant
from at_tutoring_skills.core.errors.models import CommonMistake
from at_tutoring_skills.core.service.simulation.subservice.function.models.models import FunctionParameterRequest
from at_tutoring_skills.core.service.simulation.subservice.function.models.models import FunctionRequest
from at_tutoring_skills.core.service.simulation.subservice.resource.models.models import ResourceAttributeRequest
from at_tutoring_skills.core.service.simulation.subservice.resource.models.models import ResourceRequest
from at_tutoring_skills.core.service.simulation.subservice.resource_type.models.models import (
    ResourceTypeAttributeRequest,
)
from at_tutoring_skills.core.service.simulation.subservice.resource_type.models.models import ResourceTypeRequest
from at_tutoring_skills.core.service.simulation.subservice.template.models.models import IrregularEventBody
from at_tutoring_skills.core.service.simulation.subservice.template.models.models import IrregularEventGenerator
from at_tutoring_skills.core.service.simulation.subservice.template.models.models import IrregularEventRequest
from at_tutoring_skills.core.service.simulation.subservice.template.models.models import OperationBody
from at_tutoring_skills.core.service.simulation.subservice.template.models.models import OperationRequest
from at_tutoring_skills.core.service.simulation.subservice.template.models.models import RelevantResourceRequest
from at_tutoring_skills.core.service.simulation.subservice.template.models.models import RuleBody
from at_tutoring_skills.core.service.simulation.subservice.template.models.models import RuleRequest
from at_tutoring_skills.core.service.simulation.subservice.template.models.models import TemplateMetaRequest
from at_tutoring_skills.core.task.descriptions import DescriptionsService

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
            id=reference_data["id"],
            name=reference_data["name"],
            resource_type_id_str=reference_data["resource_type_id_str"],
            attributes=attributes,
        )

    async def get_template_reference(self, task: Task) -> Union[IrregularEventRequest, RuleRequest, OperationRequest]:
        """
        Получение эталонного шаблона (template reference) из task.object_reference.
        """
        # Проверяем тип task.object_reference и преобразуем его в словарь
        if isinstance(task.object_reference, str):
            try:
                reference_data = json.loads(task.object_reference)
            except json.JSONDecodeError as e:
                raise ValueError(f"Неверный формат JSON в task.object_reference: {e}")
        elif isinstance(task.object_reference, dict):
            reference_data = task.object_reference
        else:
            raise ValueError("task.object_reference должен быть строкой JSON или словарём")

        # Определяем тип шаблона
        template_type = reference_data["meta"]["type"]
        pydantic_class = self._get_template_class(template_type)

        # Преобразуем данные в соответствующую Pydantic модель
        if pydantic_class == IrregularEventRequest:
            generator_data = reference_data["generator"]
            body_data = reference_data["body"]

            return IrregularEventRequest(
                meta=TemplateMetaRequest(
                    id=reference_data["meta"]["id"],
                    name=reference_data["meta"]["name"],
                    type=template_type,
                    rel_resources=[
                        RelevantResourceRequest(**res_data) for res_data in reference_data["meta"]["rel_resources"]
                    ],
                ),
                generator=IrregularEventGenerator(
                    type=generator_data["type"],
                    value=generator_data["value"],
                    dispersion=generator_data["dispersion"],
                ),
                body=IrregularEventBody(body=body_data["body"]),
            )

        elif pydantic_class == RuleRequest:
            body_data = reference_data["body"]

            return RuleRequest(
                meta=TemplateMetaRequest(
                    id=reference_data["meta"]["id"],
                    name=reference_data["meta"]["name"],
                    type=template_type,
                    rel_resources=[
                        RelevantResourceRequest(**res_data) for res_data in reference_data["meta"]["rel_resources"]
                    ],
                ),
                body=RuleBody(
                    condition=body_data["condition"],
                    body=body_data["body"],
                ),
            )

        elif pydantic_class == OperationRequest:
            body_data = reference_data["body"]

            return OperationRequest(
                meta=TemplateMetaRequest(
                    id=reference_data["meta"]["id"],
                    name=reference_data["meta"]["name"],
                    type=template_type,
                    rel_resources=[
                        RelevantResourceRequest(**res_data) for res_data in reference_data["meta"]["rel_resources"]
                    ],
                ),
                body=OperationBody(
                    condition=body_data["condition"],
                    body_before=body_data["body_before"],
                    delay=body_data["delay"],
                    body_after=body_data["body_after"],
                ),
            )

        else:
            raise ValueError(f"Неизвестный тип шаблона: {template_type}")

    def _get_template_class(self, template_type: str):
        """
        Возвращает соответствующий класс Pydantic на основе типа шаблона.
        """
        type_to_class = {
            "IRREGULAR_EVENT": IrregularEventRequest,
            "RULE": RuleRequest,
            "OPERATION": OperationRequest,
        }
        pydantic_class = type_to_class.get(template_type)
        if not pydantic_class:
            raise ValueError(f"Неизвестный тип шаблона: {template_type}")
        return pydantic_class

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

    async def get_all_tasks(self, variant_id: int = None, task_object: int | SUBJECT_CHOICES = None) -> models.QuerySet[Task]:
        """
        Получает все задания для заданного варианта (variant).
        """
        if variant_id is None:
            result = Task.objects.all()
        else:
            variant = await Variant.objects.aget(pk=variant_id)
            result = variant.task.all()
        
        if task_object:
            result = result.filter(task_object=task_object)
        return result

    async def get_variant_tasks_description(self, user: User, skip_completed=True, task_object: int | SUBJECT_CHOICES = None) -> str:
        """
        Возвращает описание заданий для указанного пользователя.
        """
        tasks = await self.get_all_tasks(user.variant_id, task_object=task_object)

        if not await tasks.aexists():
            return "### Для текущего этапа все задания выполнены"

        result = ""
        completed_result = ""
        async for task in tasks:
            task_user = await TaskUser.objects.filter(user=user, task=task).afirst()

            if not task_user or not task_user.is_completed:
                result += await self.get_task_description(task, user)
            elif task_user and task_user.is_completed:
                completed_result += await self.get_task_description(task, user, short=True)

        if not result:
            return "### Для текущего этапа все задания выполнены \n\n" + completed_result

        result = "### На текуий момент необходимо выполнить следующие задания: \n\n" + result

        if not skip_completed:
            if completed_result:
                return result + "### Выполнено: \n\n" + completed_result

        return result

    async def get_task_description(self, task: Task, user: User | None, short=False) -> str:
        """
        Возвращает описание задания в виде строки.
        """
        if task.task_object in DescriptionsService.KB_SUBJECT_TO_MODEL:
            return await DescriptionsService().get_kb_task_description(task, user)

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
        Создает нового пользователя или возвращает существующего.
        Для существующего пользователя вариант никогда не изменяется.

        Args:
            auth_token: Уникальный идентификатор пользователя

        Returns:
            tuple[User, bool]: Кортеж (объект пользователя, флаг создания)
        """
        try:
            # Пытаемся сначала найти существующего пользователя
            existing_user = await User.objects.filter(user_id=auth_token).afirst()

            if existing_user:
                logger.debug(f"User already exists: {auth_token}")
                return existing_user, False

            # Если пользователь не существует, создаем нового со случайным вариантом
            random_variant = await Variant.objects.order_by("?").afirst()

            user = await User.objects.acreate(user_id=auth_token, variant=random_variant)

            logger.info(
                f"Created new user: {auth_token} with variant: {random_variant.name if random_variant else 'None'}"
            )
            return user, True

        except Exception as e:
            logger.error(f"Error creating user {auth_token}: {str(e)}")
            raise

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

    async def create_task_user_entries(self, user: User) -> list[TaskUser]:
        """
        Создает записи в таблице TaskUser для всех заданий, связанных с вариантом пользователя.
        Если запись для пары (task, user) уже существует - она не изменяется.

        Args:
            user: Объект пользователя

        Returns:
            list[TaskUser]: Список созданных записей TaskUser

        Raises:
            ValueError: Если у пользователя не назначен вариант
        """
        user = await User.objects.select_related("variant").aget(user_id=user.user_id)
        if not user.variant:
            raise ValueError(f"User {user.user_id} has no variant assigned")

        try:
            # Получаем все задания, связанные с вариантом пользователя через M2M связь
            # Вариант 1: через прямое обращение к связанным задачам
            tasks = []
            async for task in user.variant.task.all():
                tasks.append(task)

            # Или Вариант 2: через явный запрос
            # tasks = []
            # async for task in Task.objects.filter(variant__id=user.variant_id):
            #     tasks.append(task)

            created_entries = []
            for task in tasks:
                # Используем get_or_create чтобы не перезаписывать существующие записи
                task_user, created = await TaskUser.objects.aget_or_create(
                    task=task, user=user, defaults={"attempts": 0, "is_completed": False}
                )
                if created:
                    created_entries.append(task_user)
                    logger.debug(f"Created TaskUser entry for task {task.id} and user {user.user_id}")
                else:
                    logger.debug(f"TaskUser entry already exists for task {task.id} and user {user.user_id}")

            logger.info(f"Created {len(created_entries)} new TaskUser entries for user {user.user_id}")
            return created_entries

        except Exception as e:
            logger.error(f"Error creating TaskUser entries for user {user.user_id}: {str(e)}")
            raise
