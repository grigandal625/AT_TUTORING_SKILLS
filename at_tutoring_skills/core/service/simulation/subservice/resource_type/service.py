from typing import List

from at_tutoring_skills.core.errors.models import CommonMistake
from at_tutoring_skills.core.service.simulation.subservice.resource_type.dependencies import IMistakeService
from at_tutoring_skills.core.service.simulation.subservice.resource_type.dependencies import ITaskService
from at_tutoring_skills.core.service.simulation.subservice.resource_type.models.models import (
    ResourceTypeAttributeRequest,
)
from at_tutoring_skills.core.service.simulation.subservice.resource_type.models.models import ResourceTypeRequest
from at_tutoring_skills.core.service.simulation.utils.utils import pydantic_mistakes


class ResourceTypeService:
    def __init__(
        self,
        mistake_service: IMistakeService,
        task_service: ITaskService,
    ):
        self._mistake_service = mistake_service
        self._task_service = task_service

    async def handle_syntax_mistakes(self, user_id: int, data: dict) -> ResourceTypeRequest:
        result = pydantic_mistakes(
            user_id=123,
            raw_request=data["args"]["resourceType"],
            pydantic_class=ResourceTypeRequest,
            pydantic_class_name="resource_type",
        )

        print("Данные, полученные pydentic моделью: ", result)

        if isinstance(result, ResourceTypeRequest):
            return result
        elif isinstance(result, list) and all(isinstance(err, CommonMistake) for err in result):
            for mistake in result:
                self._mistake_service.create_mistake(mistake, user_id, "syntax")

            raise ValueError("Handle resource type: syntax mistakes")

        raise TypeError("Handle resource type: unexpected result")

    def handle_logic_mistakes(
        self,
        user_id: int,
        resource_type: ResourceTypeRequest,
    ) -> None:
        try:
            # task = self.task_service.get_task_by_name(kb_type.id)
            # et_type = self.task_service.get_type_reference(task)
            # object_reference = self._task_service.get_object_reference(
            #     resource_type.name,
            #     ResourceTypeRequest,
            # )

            # Фиктивный объект object_reference
            object_reference = ResourceTypeRequest(
                id=1,
                name="type1",
                type="constant",
                attributes=[
                    ResourceTypeAttributeRequest(id=1, name="attr0", type="INT", enum_values_set=None, default_value=5),
                    ResourceTypeAttributeRequest(
                        id=2, name="attr2", type="INT", enum_values_set=None, default_value=5.0
                    ),
                    ResourceTypeAttributeRequest(
                        id=3, name="attr3", type="BOOL", enum_values_set=None, default_value=True
                    ),
                    ResourceTypeAttributeRequest(
                        id=4, name="attr4", type="ENUM", enum_values_set=["hello", "world"], default_value="hello"
                    ),
                ],
            )
            print("Данные object reference, полученные для сравнения: ", object_reference)

        except ValueError:  # NotFoundError
            return

        mistakes = self._attributes_logic_mistakes(
            resource_type.attributes,
            object_reference.attributes,
            # user_id,
        )
        print("Найденные ошибки: ", mistakes)

        if len(mistakes) != 0:
            for mistake in mistakes:
                self._mistake_service.create_mistake(mistake, user_id, "logic")

            return mistakes  # raise ValueError("Handle resource type: logic mistakes")

    def handle_lexic_mistakes(
        self,
        user_id: int,
        resource_type: ResourceTypeRequest,
    ) -> None:
        try:
            # object_reference = self._task_service.get_object_reference(
            #     resource_type.name,
            #     ResourceTypeRequest,
            # )
            # Фиктивный объект object_reference
            object_reference = ResourceTypeRequest(
                id=1,
                name="type1",
                type="constant",
                attributes=[
                    ResourceTypeAttributeRequest(id=1, name="attr0", type="INT", enum_values_set=None, default_value=5),
                    ResourceTypeAttributeRequest(
                        id=2, name="attr2", type="INT", enum_values_set=None, default_value=5.0
                    ),
                    ResourceTypeAttributeRequest(
                        id=3, name="attr3", type="BOOL", enum_values_set=None, default_value=True
                    ),
                    ResourceTypeAttributeRequest(
                        id=4, name="attr4", type="ENUM", enum_values_set=["hello", "world"], default_value="hello"
                    ),
                ],
            )
            print("Данные object reference, полученные для сравнения: ", object_reference)

        except ValueError:  # NotFoundError
            return

        mistakes = self._attributes_lexic_mistakes(
            resource_type.attributes,
            object_reference.attributes,
        )

        if len(mistakes) != 0:
            for mistake in mistakes:
                self._mistake_service.create_mistake(mistake, user_id, "lexic")

            return mistakes  # raise ValueError("Handle resource type: lexic mistakes")

    def _attributes_logic_mistakes(
        self,
        attrs: List[ResourceTypeAttributeRequest],
        attrs_reference: List[ResourceTypeAttributeRequest],
        # user_id = 123,
    ) -> List[CommonMistake]:
        mistakes = []
        match_attrs_count = 0
        user_id = 123

        # Проверка на количество атрибутов
        print(f"Comparing number of attributes: provided={len(attrs)}, reference={len(attrs_reference)}")
        if len(attrs) != len(attrs_reference):
            mistake = CommonMistake(
                user_id=user_id,
                type="logic",
                task_id=None,
                fine=0.0,
                coefficient=1.0,
                tip="Check the number of attributes.",
                is_tip_shown=False,
                message="Wrong number of attributes provided.",
            )

            mistakes.append(mistake)

        # Преобразование эталонных атрибутов в словарь для быстрого поиска
        attrs_reference_dict = {attr.name: attr for attr in attrs_reference}
        print(f"Reference attributes dictionary: {attrs_reference_dict}")

        for attr in attrs:
            print(f"\nProcessing attribute: name={attr.name}, type={attr.type}, default_value={attr.default_value}")

            if attr.name not in attrs_reference_dict:
                # print(f"Unknown attribute found: {attr.name}")
                # mistake = CommonMistake(
                #     user_id=user_id,
                #     type="logic",
                #     task_id=None,
                #     fine=0.0,
                #     coefficient=1.0,
                #     tip=f"Unknown attribute '{attr.name}'.",
                #     is_tip_shown=False,
                #     message=f"Unknown attribute.",
                # )
                # mistakes.append(mistake)
                continue

            attr_reference = attrs_reference_dict[attr.name]
            print(
                f"Found reference attribute: name={attr_reference.name}, type={attr_reference.type}, default_value={attr_reference.default_value}"
            )

            # Проверка типа атрибута
            if attr.type != attr_reference.type:
                print(
                    f"Type mismatch for attribute '{attr.name}': provided={attr.type}, reference={attr_reference.type}"
                )
                mistake = CommonMistake(
                    user_id=user_id,
                    type="logic",
                    task_id=None,
                    fine=0.0,
                    coefficient=1.0,
                    tip=f"Invalid attribute type '{attr.name}'.",
                    is_tip_shown=False,
                    message=f"Invalid attribute type.",
                )
                mistakes.append(mistake)
                continue

            # Проверка значения по умолчанию
            if attr.default_value != attr_reference.default_value:
                print(
                    f"Default value mismatch for attribute '{attr.name}': provided={attr.default_value}, reference={attr_reference.default_value}"
                )
                mistake = CommonMistake(
                    user_id=user_id,
                    type="logic",
                    task_id=None,
                    fine=0.0,
                    coefficient=1.0,
                    tip=f"Invalid attribute default value '{attr.name}'.",
                    is_tip_shown=False,
                    message=f"Invalid attribute default value.",
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
            mistake = CommonMistake(
                user_id=user_id,
                type="logic",
                task_id=None,
                fine=0.0,
                coefficient=1.0,
                tip=f"Missing required attribute '{attr_name}'.",
                is_tip_shown=False,
                message=f"Missing required attribute.",
            )
            mistakes.append(mistake)

        return mistakes

    def _attributes_lexic_mistakes(
        self,
        attrs: List[ResourceTypeAttributeRequest],
        attrs_reference: List[ResourceTypeAttributeRequest],
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
                mistake = CommonMistake(
                    user_id=123,
                    type="lexic",
                    task_id=None,
                    fine=0.0,
                    coefficient=1.0,
                    tip=f"Attribute naming error: '{attr.name}' is not found, but '{closest_match}' is close.",
                    is_tip_shown=False,
                    message=f"Attribute naming error.",
                )
                mistakes.append(mistake)

            else:
                mistake = CommonMistake(
                    user_id=123,  # Замените на актуальное значение user_id
                    type="lexic",
                    task_id=None,
                    fine=0.0,
                    coefficient=1.0,
                    tip=f"Unknown attribute: '{attr.name}' is not found in the reference.",
                    is_tip_shown=False,
                    message=f"Unknown attribute.",
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
