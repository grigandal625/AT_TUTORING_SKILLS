from typing import List

from pydantic import ValidationError
from pydantic_core import ErrorDetails

from at_tutoring_skills.core.errors.consts import SIMULATION_COEFFICIENTS
from at_tutoring_skills.core.errors.conversions import to_syntax_mistake
from at_tutoring_skills.core.errors.models import CommonMistake
from at_tutoring_skills.core.service.simulation.subservice.resource_type.dependencies import (
    IMistakeService,
    ITaskService,
)
from at_tutoring_skills.core.service.simulation.subservice.resource_type.models.models import (
    ResourceTypeAttributeRequest,
    ResourceTypeRequest,
)
from at_tutoring_skills.core.service.simulation.utils.utils import pydantic_mistakes


class ResourceTypeService:
    def __init__(
        self,
        mistake_service: IMistakeService,
        task_service: ITaskService,
    ):
        self._mistake_service = mistake_service
        self._task_service = task_service

    def handle_syntax_mistakes(
        self,
        user_id: int,
        raw_request: dict,
    ) -> ResourceTypeRequest:
        result = pydantic_mistakes(
            user_id=123,
            raw_request=raw_request,
            pydantic_class=ResourceTypeRequest,
            pydantic_class_name="resource_type",
        )

        if isinstance(result, ResourceTypeRequest):
            return result

        elif isinstance(result, list) and all(
            isinstance(err, CommonMistake) for err in result
        ):
            for mistake in result:
                self._mistake_service.create_mistake(mistake, user_id)

            raise ValueError("Handle resource type: syntax mistakes")

        raise TypeError("Handle resource type: unexpected result")

    def handle_logic_mistakes(
        self,
        user_id: int,
        resource_type: ResourceTypeRequest,
    ) -> None:
        try:
            object_reference = self._task_service.get_object_reference(
                resource_type.name,
                ResourceTypeRequest,
            )

        except ValueError:  # NotFoundError
            return

        mistakes = self._attributes_logic_mistakes(
            resource_type.attributes,
            object_reference.attributes,
        )

        if len(mistakes) != 0:
            for mistake in mistakes:
                self._mistake_service.create_mistake(mistake, user_id)

            raise ValueError("Handle resource type: logic mistakes")

    def handle_lexic_mistakes(
        self,
        user_id: int,
        resource_type: ResourceTypeRequest,
    ) -> None:
        try:
            object_reference = self._task_service.get_object_reference(
                resource_type.name,
                ResourceTypeRequest,
            )

        except ValueError:  # NotFoundError
            return

        mistakes = self._attributes_lexic_mistakes(
            resource_type.attributes,
            object_reference.attributes,
        )

        if len(mistakes) != 0:
            for mistake in mistakes:
                self._mistake_service.create_mistake(mistake, user_id)

            raise ValueError("Handle resource type: lexic mistakes")

    def _attributes_logic_mistakes(
        self,
        attrs: List[ResourceTypeAttributeRequest],
        attrs_reference: List[ResourceTypeAttributeRequest],
    ) -> List[CommonMistake]:   
        mistakes: List[CommonMistake] = []
        match_attrs_count = 0

        if len(attrs) != len(attrs_reference):
            mistake = CommonMistake(
                message=f"Wrong number of attributes provided.",
            )
            mistakes.append(mistake)

        for attr in attrs:
            find_flag = False
            for attr_reference in attrs_reference:
                if attr.name == attr_reference.name:
                    find_flag = True
                    match_attrs_count += 1
                    if attr.type != attr_reference.type:
                        mistake = CommonMistake(
                            message=f"Invalid attribute type'{attr.name}'.",
                        )
                        mistakes.append(mistake)
                        continue

                    if attr.default_value != attr_reference.default_value:
                        mistake = CommonMistake(
                            message=f"Invalid attribute default value'{attr.name}'.",
                        )
                    mistakes.append(mistake)
                    break

            if not find_flag:
                mistake = CommonMistake(
                    message=f"Unknown attribute'{attr.name}'.",
                )
                mistakes.append(mistake)
        
        if match_attrs_count < len(attrs_reference):
            mistake = CommonMistake(
                message=f"Missing required attributes.",
            )
            mistakes.append(mistake)

        return mistakes
    

    def _attributes_lexic_mistakes(
        self,
        attrs: List[ResourceTypeAttributeRequest],
        attrs_reference: List[ResourceTypeAttributeRequest],
    ) -> List[CommonMistake]:   
        
        mistakes: List[CommonMistake] = []
        match_attrs_count = 0

        for attr in attrs:
            find_flag = False
            for attr_reference in attrs_reference:
                if attr.name == attr_reference.name:
                    break
                else: ...

        return mistakes
    

    @staticmethod
    def _levenshtein_distance(s1: str, s2: str) -> int:
        """Calculate the minimum edit distance between two strings"""
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