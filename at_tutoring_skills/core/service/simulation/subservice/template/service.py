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
    ) -> List[CommonMistake]: ...

    def _attributes_lexic_mistakes(
        self,
        attrs: List[ResourceTypeAttributeRequest],
        attrs_reference: List[ResourceTypeAttributeRequest],
    ) -> List[CommonMistake]: ...
