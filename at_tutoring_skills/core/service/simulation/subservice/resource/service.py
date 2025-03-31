from typing import List


from at_tutoring_skills.core.errors.models import CommonMistake
from at_tutoring_skills.core.service.simulation.subservice.resource.dependencies import IMistakeService
from at_tutoring_skills.core.service.simulation.subservice.resource.dependencies import IResourceTypeComponent
from at_tutoring_skills.core.service.simulation.subservice.resource.dependencies import ITaskService
from at_tutoring_skills.core.service.simulation.subservice.resource.models.models import (
    ResourceAttributeRequest,
    ResourceRequest
)
from at_tutoring_skills.core.service.simulation.subservice.resource_type.models.models import ResourceTypeRequest
from at_tutoring_skills.core.service.simulation.utils.utils import pydantic_mistakes


class ResourceService: 
    def __init__(
        self,
        mistake_service: IMistakeService,
        task_service: ITaskService,
        object_resource_type_service: IResourceTypeComponent,
    ):
        self._mistake_service = mistake_service
        self._task_service = task_service
        self._object_resource_type_service = object_resource_type_service

    def handle_syntax_mistakes(
        self,
        user_id: int,
        data: dict,
    ) -> ResourceRequest:
        result = pydantic_mistakes(
            user_id=123,
            raw_request=data['args']['resource'],
            pydantic_class=ResourceRequest,
            pydantic_class_name="resource",
        )

        print("Данные, полученные pydentic моделью: ", result)

        if isinstance(result, ResourceRequest):
            return result

        elif isinstance(result, list) and all(isinstance(err, CommonMistake) for err in result):
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

            object_resource_type_reference = self._object_resource_type_service.get_object_reference(
                resource.rta_id,
                ResourceTypeRequest,
            )

        except ValueError:  # NotFoundError
            return

        mistakes = self._attributes_logic_mistakes(
            object_resource_type_reference.name,
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

    # надо дописать, чтобы из базы данныхт по id доставалось имя тип ресурса и проверялось оно или не оно

    def _attributes_logic_mistakes(
        self,
        resource_type: ResourceTypeRequest,
        attrs: List[ResourceAttributeRequest],
        attrs_reference: List[ResourceAttributeRequest],
    ) -> List[CommonMistake]:
        mistakes: List[CommonMistake] = []
        match_attrs_count = 0

        if resource_type.name != attrs_reference.name:  # type_id_attrs_reference:
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
    ) -> List[CommonMistake]:
        ...
