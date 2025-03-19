from typing import List

from pydantic import ValidationError
from pydantic_core import ErrorDetails

from at_tutoring_skills.core.errors.consts import SIMULATION_COEFFICIENTS
from at_tutoring_skills.core.errors.conversions import to_syntax_mistake
from at_tutoring_skills.core.errors.models import CommonMistake
from at_tutoring_skills.core.service.simulation.subservice.resource.dependencies import (
    IMistakeService,
    IResourceTypeComponent,
    ITaskService,
)
from at_tutoring_skills.core.service.simulation.subservice.resource.models.models import (
    ResourceAttributeRequest,
    ResourceRequest,
)
from at_tutoring_skills.core.service.simulation.utils.utils import pydantic_mistakes


class ResourceService:
    def __init__(
        self,
        mistake_service: IMistakeService,
        task_service: ITaskService,
        resource_type_component: IResourceTypeComponent,
    ):
        self._mistake_service = mistake_service
        self._task_service = task_service
        self._resource_type_component = resource_type_component

    def handle_syntax_mistakes(
        self,
        user_id: int,
        raw_request: dict,
    ) -> ResourceRequest:
        result = pydantic_mistakes(
            user_id=123,
            raw_request=raw_request,
            pydantic_class=ResourceRequest,
            pydantic_class_name="resource",
        )

        if isinstance(result, ResourceRequest):
            return result

        elif isinstance(result, list) and all(
            isinstance(err, CommonMistake) for err in result
        ):
            for mistake in result:
                self._mistake_service.create_mistake(mistake, user_id)

            raise ValueError("Handle resource: syntax mistakes")

        raise TypeError("Handle resource: unexpected result")

    def handle_logic_mistakes(
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

        mistakes = self._attributes_logic_mistakes(
            resource.resource_type_id,
            object_reference.resource_type_id,
            resource.attributes,
            object_reference.attributes,
        )

        if len(mistakes) != 0:
            for mistake in mistakes:
                self._mistake_service.create_mistake(mistake, user_id)

            raise ValueError("Handle resource: logic mistakes")

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

    def _attributes_logic_mistakes(
        self,
        object: ResourceRequest,
        object_reference: ResourceRequest,
    ) -> List[CommonMistake]:
        mistakes: List[CommonMistake] = []
        match_attrs_count = 0
        
        # ПРИМЕР
        resource_type = self._resource_type_component.get_resource_type(object.id)

        if type_id.resource_type_id != type_id_attrs_reference:
            mistake = CommonMistake(
                message=f"Wrong type of resource provided.",
            )
            mistakes.append(mistake)
            return mistakes

        for attr in attrs:
            for attr_reference in attrs_reference:
                if attr.name == attr_reference.name:
                    if attr.value != attr_reference.value:
                        mistake = CommonMistake(
                            message=f"Invalid attribute default value'{attr.name}'.",
                        )
                    mistakes.append(mistake)
                    break

        return mistakes

    def _attributes_lexic_mistakes(
        self,
        attrs: List[ResourceAttributeRequest],
        attrs_reference: List[ResourceAttributeRequest],
    ) -> List[CommonMistake]: ...
