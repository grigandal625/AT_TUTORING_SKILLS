from typing import List

from at_tutoring_skills.apps.skills.models import SUBJECT_CHOICES
from at_tutoring_skills.apps.skills.models import Task
from at_tutoring_skills.core.errors.consts import SIMULATION_COEFFICIENTS
from at_tutoring_skills.core.errors.conversions import to_lexic_mistake, to_syntax_mistake
from at_tutoring_skills.core.errors.conversions import to_logic_mistake
from at_tutoring_skills.core.errors.models import CommonMistake
from at_tutoring_skills.core.service.simulation.subservice.resource_type.dependencies import IMistakeService
from at_tutoring_skills.core.service.simulation.subservice.resource_type.dependencies import ITaskService
from at_tutoring_skills.core.service.simulation.subservice.resource_type.models.models import (
    ResourceTypeAttributeRequest,
)
from at_tutoring_skills.core.service.simulation.subservice.resource_type.models.models import ResourceTypeRequest
from at_tutoring_skills.core.service.simulation.utils.utils import pydantic_mistakes
from at_tutoring_skills.core.task.service import TaskService


class ResourceTypeService:
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

    async def handle_syntax_mistakes(self, user_id: int, data: dict) -> ResourceTypeRequest:
        result = pydantic_mistakes(
            user_id=user_id,
            raw_request=data["args"]["resourceType"],
            pydantic_class=ResourceTypeRequest,
            pydantic_class_name="resource_type",
        )
        errors_list = []

        print("Данные, полученные pydentic моделью: ", result)

        if isinstance(result, ResourceTypeRequest):
            return result
        elif isinstance(result, list) and all(isinstance(err, CommonMistake) for err in result):
            for mistake in result:
                # await self.main_task_service.append_mistake(mistake)
                # self._mistake_service.create_mistake(mistake, user_id, "syntax")

                common_mistake = to_syntax_mistake(
                        user_id=user_id,
                        tip=f"Синтаксическая ошибка при создании типа ресурса.\n\n",
                        coefficients=SIMULATION_COEFFICIENTS,
                        entity_type="resource_type",
                        skills=[270],
                )
                errors_list.append(common_mistake)
                await self.main_task_service.append_mistake(common_mistake)

            raise ValueError("Синтаксическая ошибка при создании типа ресурса")



    async def handle_logic_mistakes(
        self,
        user_id: int,
        resource_type: ResourceTypeRequest,
    ) -> None:
        try:
            task: Task = await self.main_task_service.get_task_by_name(
                resource_type.name, SUBJECT_CHOICES.SIMULATION_RESOURCE_TYPES
            )
            task_id = task.pk
            object_reference = await self.main_task_service.get_resource_type_reference(task)

            print("Данные object reference, полученные для сравнения: ", object_reference)

        except ValueError:  # NotFoundError
            print("Создан тип ресурса, не касающийся задания")
            return

        mistakes = self._attributes_logic_mistakes(
            resource_type,
            object_reference,
            resource_type.attributes,
            object_reference.attributes,
            user_id,
            task_id,
        )
        print("Найденные ошибки: ", mistakes)

        if len(mistakes) != 0:
            for mistake in mistakes:
                await self.main_task_service.append_mistake(mistake)

            return mistakes  # raise ValueError("Handle resource type: logic mistakes")

    async def handle_lexic_mistakes(
        self,
        user_id: int,
        resource_type: ResourceTypeRequest,
    ) -> None:
        try:
            task: Task = await self.main_task_service.get_task_by_name(
                resource_type.name, SUBJECT_CHOICES.SIMULATION_RESOURCE_TYPES
            )
            task_id = task.pk
            object_reference = await self.main_task_service.get_resource_type_reference(task)

            print("Данные object reference, полученные для сравнения: ", object_reference)

        except ValueError:  # NotFoundError
            return

        mistakes = self._attributes_lexic_mistakes(
            resource_type.attributes,
            object_reference.attributes,
            user_id,
            task_id,
        )

        if len(mistakes) != 0:
            for mistake in mistakes:
                await self.main_task_service.append_mistake(mistake)

            return mistakes  # raise ValueError("Handle resource type: lexic mistakes")

    def _attributes_logic_mistakes(
        self,
        resource_type: ResourceTypeRequest,
        resource_type_reference: ResourceTypeRequest,
        attrs: List[ResourceTypeAttributeRequest],
        attrs_reference: List[ResourceTypeAttributeRequest],
        user_id: int,
        task_id: int,
    ) -> List[CommonMistake]:
        mistakes = []
        match_attrs_count = 0

        print(f"Comparing resource type: provided={resource_type.type}, reference={resource_type_reference.type}")
        if resource_type.type != resource_type_reference.type:
            mistake = to_logic_mistake(
                user_id=user_id,
                task_id=task_id,
                tip="Указан неправильный тип типа ресурса.\n\n",
                coefficients=SIMULATION_COEFFICIENTS,
                entity_type="resource_type",
                skills=[221],
            )
            mistakes.append(mistake)
            return mistakes

        print(f"Comparing number of attributes: provided={len(attrs)}, reference={len(attrs_reference)}")
        if len(attrs) != len(attrs_reference):
            mistake = to_logic_mistake(
                user_id=user_id,
                task_id=task_id,
                tip="Указано неправильное количество атрибутов.\n\n",
                coefficients=SIMULATION_COEFFICIENTS,
                entity_type="resource_type",
                skills=[222, 223, 224],
            )
            mistakes.append(mistake)

        attrs_reference_dict = {attr.name: attr for attr in attrs_reference}
        print(f"Reference attributes dictionary: {attrs_reference_dict}")

        for attr in attrs:
            print(f"\nProcessing attribute: name={attr.name}, type={attr.type}, default_value={attr.default_value}")

            if attr.name not in attrs_reference_dict:
                continue

            attr_reference = attrs_reference_dict[attr.name]
            print(
                f"Found reference attribute: name={attr_reference.name}, type={attr_reference.type}, default_value={attr_reference.default_value}"
            )

            if attr.type != attr_reference.type:
                print(
                    f"Type mismatch for attribute '{attr.name}': provided={attr.type}, reference={attr_reference.type}"
                )
                mistake = to_logic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip=f"Недопустимый тип атрибута {attr.name}.\n\n",
                    coefficients=SIMULATION_COEFFICIENTS,
                    entity_type="resource_type",
                    skills=[223, 224],
                )
                mistakes.append(mistake)
                continue

            if attr.default_value != attr_reference.default_value:
                print(
                    f"Default value mismatch for attribute '{attr.name}': provided={attr.default_value}, reference={attr_reference.default_value}"
                )
                tip = f"Недопустимое значение атрибута по умолчанию '{attr.name}'.\n\n"
                mistake = to_logic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip=tip,
                    coefficients=SIMULATION_COEFFICIENTS,
                    entity_type="resource_type",
                    skills=[224],
                )
                mistakes.append(mistake)
                continue

            # Проверка enum_values_set для типа ENUM
            if attr.type == "BaseTypesEnum.ENUM":
                if not isinstance(attr.enum_values_set, list) or not all(
                    isinstance(value, str) for value in attr.enum_values_set
                ):
                    print(f"Invalid enum_values_set for attribute '{attr.name}': provided={attr.enum_values_set}")
                    mistake = to_logic_mistake(
                        user_id=user_id,
                        task_id=task_id,
                        tip=f"Некорректный формат enum для атрибута {attr.name}.\n\n",
                        coefficients=SIMULATION_COEFFICIENTS,
                        entity_type="resource_type",
                        skills=[223, 224],
                    )
                    mistakes.append(mistake)
                    continue

                if set(attr.enum_values_set) != set(attr_reference.enum_values_set):
                    print(
                        f"Enum values mismatch for attribute '{attr.name}': provided={attr.enum_values_set}, reference={attr_reference.enum_values_set}"
                    )
                    mistake = to_logic_mistake(
                        user_id=user_id,
                        task_id=task_id,
                        tip=f"Несовпадение значений enum для атрибута {attr.name}.\n\n",
                        coefficients=SIMULATION_COEFFICIENTS,
                        entity_type="resource_type",
                        skills=[224],
                    )
                    mistakes.append(mistake)
                    continue

            # Увеличиваем счётчик совпадений только при полном совпадении
            print(f"Attribute '{attr.name}' matches the reference.")
            match_attrs_count += 1

        # Проверка на отсутствующие атрибуты
        reference_attr_names = {attr.name for attr in attrs_reference}
        provided_attr_names = {attr.name for attr in attrs}

        missing_attrs = reference_attr_names - provided_attr_names
        print(f"Missing attributes: {missing_attrs}")
        for attr_name in missing_attrs:
            print(f"Missing required attribute: {attr_name}")
            mistake = to_logic_mistake(
                user_id=user_id,
                task_id=task_id,
                tip=f"Отсутствует обязательный атрибут {attr_name}.",
                coefficients=SIMULATION_COEFFICIENTS,
                entity_type="resource_type",
                skills=[222],
            )
            mistakes.append(mistake)

        return mistakes

    def _attributes_lexic_mistakes(
        self,
        attrs: List[ResourceTypeAttributeRequest],
        attrs_reference: List[ResourceTypeAttributeRequest],
        user_id: int,
        task_id: int,
    ) -> List[CommonMistake]:
        mistakes: List[CommonMistake] = []

        attrs_reference_dict = {attr.name: attr for attr in attrs_reference}

        for attr in attrs:
            if attr.name in attrs_reference_dict:
                continue

            closest_match = None
            min_distance = float("inf")
            for attr_reference in attrs_reference:
                distance = self._levenshtein_distance(attr.name, attr_reference.name)
                if distance < min_distance:
                    min_distance = distance
                    closest_match = attr_reference.name

            if closest_match and min_distance <= 1:
                mistake = to_lexic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip=f"Ошибка в имени атрибута: {attr.name} не найден, но {closest_match} является ближайшим.\n\n",
                    coefficients=SIMULATION_COEFFICIENTS,
                    entity_type="resource_type",
                    skills=[270],
                )
                mistakes.append(mistake)

            else:
                mistake = to_lexic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip=f"Неизвестный атрибут: {attr.name} не найдено.\n\n",
                    coefficients=SIMULATION_COEFFICIENTS,
                    entity_type="resource_type",
                    skills=[222],
                )
                mistakes.append(mistake)

        return mistakes

    @staticmethod
    def _levenshtein_distance(s1: str, s2: str) -> int:
        if len(s1) < len(s2):
            return ResourceTypeService._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]
