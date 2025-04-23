import json
from typing import List

from jsonschema import ValidationError

from at_tutoring_skills.apps.skills.models import SUBJECT_CHOICES
from at_tutoring_skills.apps.skills.models import Task
from at_tutoring_skills.core.errors.consts import SIMULATION_COEFFICIENTS
from at_tutoring_skills.core.errors.conversions import to_logic_mistake, to_syntax_mistake
from at_tutoring_skills.core.errors.models import CommonMistake
from at_tutoring_skills.core.service.simulation.subservice.resource.dependencies import IMistakeService
from at_tutoring_skills.core.service.simulation.subservice.resource.dependencies import ITaskService
from at_tutoring_skills.core.service.simulation.subservice.resource.models.models import ResourceAttributeRequest
from at_tutoring_skills.core.service.simulation.subservice.resource.models.models import ResourceRequest
from at_tutoring_skills.core.service.simulation.subservice.resource_type.models.models import ResourceTypeRequest
from at_tutoring_skills.core.service.simulation.utils.utils import pydantic_mistakes
from at_tutoring_skills.core.task.service import TaskService


class ResourceService:
    mistake_service = None
    main_task_service = None

    def __init__(
        self,
        mistake_service: IMistakeService,
        task_service: ITaskService,
    ):
        self._mistake_service = mistake_service
        self._task_service = task_service
        self.main_task_service = TaskService()

    async def handle_syntax_mistakes(
        self,
        user_id: int,
        data: dict,
    ) -> ResourceRequest:
        result = pydantic_mistakes(
            user_id=user_id,
            raw_request=data["args"]["resource"],
            pydantic_class=ResourceRequest,
            pydantic_class_name="resource",
        )
        errors_list = []

        print("Данные, полученные pydentic моделью: ", result)

        if isinstance(result, ResourceRequest):
            return result
        elif isinstance(result, list) and all(isinstance(err, CommonMistake) for err in result):
            for mistake in result:
                # self._mistake_service.create_mistake(mistake, user_id)

                common_mistake = to_syntax_mistake(
                        user_id=user_id,
                        tip=f"Синтаксическая ошибка при создании ресурса.",
                        coefficients=SIMULATION_COEFFICIENTS,
                        entity_type="resource_type",
                        skills=[270],
                )
                errors_list.append(common_mistake)
                await self.main_task_service.append_mistake(common_mistake)

            raise ValueError("Синтаксическая ошибка при создании ресурса")


    async def handle_logic_mistakes(
        self,
        user_id: int,
        resource: ResourceRequest,
        resource_type: str,
    ) -> None:
        try:
            try:
                if isinstance(resource_type, str):
                    # Если resource_type — строка, пытаемся разобрать её как JSON
                    resource_type_data = json.loads(resource_type)
                elif isinstance(resource_type, dict):
                    # Если resource_type уже словарь, используем его напрямую
                    resource_type_data = resource_type
                else:
                    raise ValueError("Некорректный тип данных для resource_type. Ожидалась строка или словарь.")

                # Создаем объект ResourceTypeRequest
                resource_type_obj = ResourceTypeRequest(**resource_type_data)
            except (json.JSONDecodeError, ValidationError) as e:
                print(f"Ошибка при преобразовании resource_type: {e}")
                return
            task: Task = await self.main_task_service.get_task_by_name(
                resource.name, SUBJECT_CHOICES.SIMULATION_RESOURCES
            )
            task_id = task.pk
            object_reference = await self.main_task_service.get_resource_reference(task)

            print("Данные object reference, полученные для сравнения: ", object_reference)

        except ValueError:  # NotFoundError
            print("Создан ресурс, не касающийся задания")
            return

        mistakes = self._attributes_logic_mistakes(
            resource_type_obj,
            object_reference,
            resource.attributes,
            object_reference.attributes,
            user_id,
            task_id,
        )
        print("Найденные ошибки: ", mistakes)

        if len(mistakes) != 0:
            for mistake in mistakes:
                await self.main_task_service.append_mistake(mistake)

            return mistakes  # raise ValueError("Handle resource type: logic mistakes")

    def handle_lexic_mistakes(
        self,
        user_id: int,
        resource: ResourceRequest,
    ) -> None:
        try:
            object_reference = self._task_service.get_object_reference(
                resource.name,
                ResourceRequest,
            )

        except ValueError:  # NotFoundError
            return

        mistakes = self._attributes_lexic_mistakes(
            resource.name,
            object_reference.name,
        )

        if len(mistakes) != 0:
            for mistake in mistakes:
                self._mistake_service.create_mistake(mistake, user_id)

            raise ValueError("Handle resource: lexic mistakes")

    # надо дописать, чтобы из базы данныхт по id доставалось имя тип ресурса и проверялось оно или не оно

    def _attributes_logic_mistakes(
        self,
        resource_type: ResourceTypeRequest,
        resource_reference: ResourceRequest,
        attrs: List[ResourceAttributeRequest],
        attrs_reference: List[ResourceAttributeRequest],
        user_id: int,
        task_id: int,
    ) -> List[CommonMistake]:
        mistakes: List[CommonMistake] = []
        match_attrs_count = 0

        print(f"Reference resource type: {resource_type.name}")

        if resource_type.name != resource_reference.resource_type_id_str:  # type_id_attrs_reference:
            mistake = to_logic_mistake(
                user_id=user_id,
                task_id=task_id,
                tip="Указан неправильный тип ресурса.",
                coefficients=SIMULATION_COEFFICIENTS,
                entity_type="resource",
                skills=[231],
            )
            mistakes.append(mistake)
            return mistakes

        attrs_reference_dict = {attr.name: attr for attr in attrs_reference}
        print(f"Reference attributes dictionary: {attrs_reference_dict}")

        for attr in attrs:
            if attr.name not in attrs_reference_dict:
                continue

            attr_reference = attrs_reference_dict[attr.name]
            provided_value = str(attr.value)
            reference_value = str(attr_reference.value)

            if provided_value != reference_value:
                print(
                    f"Default value mismatch for attribute {attr.name}: provided={attr.value}, reference={attr_reference.value}"
                )
                tip = f"Недопустимое значение атрибута по умолчанию {attr.name}."
                mistake = to_logic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip=tip,
                    coefficients=SIMULATION_COEFFICIENTS,
                    entity_type="resource",
                    skills=[232],
                )
                mistakes.append(mistake)
                continue

        return mistakes

    def _attributes_lexic_mistakes(
        self,
        attrs: List[ResourceAttributeRequest],
        attrs_reference: List[ResourceAttributeRequest],
    ) -> List[CommonMistake]:
        ...
