# from typing import List
# from pydantic import ValidationError
# from pydantic_core import ErrorDetails
# from at_tutoring_skills.core.errors.consts import SIMULATION_COEFFICIENTS
# from at_tutoring_skills.core.errors.conversions import to_syntax_mistake
# from at_tutoring_skills.core.errors.models import CommonMistake
# from at_tutoring_skills.core.service.simulation.subservice.template_usage.dependencies import (
#     IMistakeService,
#     ITaskService,
# )
# from at_tutoring_skills.core.service.simulation.subservice.template_usage.models.models import (
#     TemplateUsageArgumentRequest,
#     TemplateUsageRequest
# )
# from at_tutoring_skills.core.service.simulation.utils.utils import pydantic_mistakes


class TemplateUsageService:
    ...


# mistake_service = None
# main_task_service = None

# def __init__(
#     self,
#     mistake_service: IMistakeService,
#     task_service: ITaskService,
# ):
#     self._mistake_service = mistake_service
#     self._task_service = task_service
#     self.main_task_service = TaskService()


# async def handle_syntax_mistakes(
#         self,
#         user_id: int,
#         data: dict
#     ) -> TemplateUsageRequest:


#     def handle_syntax_mistakes(
#         self,
#         user_id: int,
#         raw_request: dict,
#     ) -> TemplateUsageRequest:
#         result = pydantic_mistakes(
#             user_id=123,
#             raw_request=raw_request,
#             pydantic_class=TemplateUsageRequest,
#             pydantic_class_name="template_usage",
#         )

#         if isinstance(result, TemplateUsageRequest):
#             return result

#         elif isinstance(result, list) and all(
#             isinstance(err, CommonMistake) for err in result
#         ):
#             for mistake in result:
#                 self._mistake_service.create_mistake(mistake, user_id)

#             raise ValueError("Handle template usage: syntax mistakes")

#         raise TypeError("Handle template usage type: unexpected result")

#     def handle_lexic_mistakes(
#         self,
#         user_id: int,
#         template_usage: TemplateUsageRequest,
#     ) -> None:
#         try:
#             object_reference = self._task_service.get_object_reference(
#                 template_usage.name,
#                 TemplateUsageRequest,
#             )

#         except ValueError:  # NotFoundError
#             return

#         mistakes = self._attributes_lexic_mistakes(
#             template_usage.attributes,
#             object_reference.attributes,
#         )

#         if len(mistakes) != 0:
#             for mistake in mistakes:
#                 self._mistake_service.create_mistake(mistake, user_id)

#             raise ValueError("Handle template usage: lexic mistakes")

#     def handle_logic_mistakes(
#         self,
#         user_id: int,
#         template_usage: TemplateUsageRequest,
#     ) -> None:
#         try:
#             object_reference = self._task_service.get_object_reference(
#                 template_usage.name,
#                 TemplateUsageRequest,
#             )

#         except ValueError:  # NotFoundError
#             return

#         mistakes = self._attributes_logic_mistakes(
#             template_usage.template_id,
#             object_reference.template_id,
#             template_usage.arguments,
#             object_reference.arguments,
#         )

#         if len(mistakes) != 0:
#             for mistake in mistakes:
#                 self._mistake_service.create_mistake(mistake, user_id)

#             raise ValueError("Handle template usage: logic mistakes")


#     def _attributes_logic_mistakes(
#         self,
#         id_template: TemplateUsageRequest,
#         id_template_reference: TemplateUsageRequest,
#         attrs: List[TemplateUsageArgumentRequest],
#         attrs_reference: List[TemplateUsageArgumentRequest],
#     ) -> List[CommonMistake]:
#         mistakes: List[CommonMistake] = []
#         match_attrs_count = 0

#         if id_template != id_template_reference:
#             mistake = CommonMistake(
#                 message=f"Wrong template provided.",
#             )
#             mistakes.append(mistake)
#             return mistakes

#         for attr in attrs:
#             find_flag = False
#             for attr_reference in attrs_reference:
#                 if attr.name == attr_reference.name:
#                     find_flag = True
#                     match_attrs_count += 1
#                     if attr.type != attr_reference.type:
#                         mistake = CommonMistake(
#                             message=f"Invalid attribute type'{attr.name}'.",
#                         )
#                         mistakes.append(mistake)
#                         continue

#                     if attr.default_value != attr_reference.default_value:
#                         mistake = CommonMistake(
#                             message=f"Invalid attribute default value'{attr.name}'.",
#                         )
#                     mistakes.append(mistake)
#                     break

#             if not find_flag:
#                 mistake = CommonMistake(
#                     message=f"Unknown attribute'{attr.name}'.",
#                 )
#                 mistakes.append(mistake)

#         if match_attrs_count < len(attrs_reference):
#             mistake = CommonMistake(
#                 message=f"Missing required attributes.",
#             )
#             mistakes.append(mistake)

#         return mistakes


#     def _attributes_lexic_mistakes(
#         self,
#         attrs: List[TemplateUsageRequest],
#         attrs_reference: List[TemplateUsageRequest],
#     ) -> List[CommonMistake]:  ...

from typing import List, Type

from pydantic import BaseModel

from at_tutoring_skills.core.errors.models import CommonMistake

from at_tutoring_skills.core.service.simulation.subservice.template.dependencies import (
    IMistakeService,
    ITaskService,
    IResourceTypeComponent,
)

from at_tutoring_skills.core.service.simulation.subservice.template.models.models import (
    RelevantResourceRequest,
    TemplateMetaRequest,
    IrregularEventRequest,
    OperationRequest,
    RuleRequest,
)

from at_tutoring_skills.core.service.simulation.subservice.resource_type.models.models import (
    ResourceTypeRequest,
)

from at_tutoring_skills.core.service.simulation.utils.utils import pydantic_mistakes


class TemplateService:
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
        raw_request: dict,
    ) -> TemplateMetaRequest:
        template_type = raw_request.get("type")

        model_mapping: dict[str, Type[BaseModel]] = {
            "IRREGULAR_EVENT": IrregularEventRequest,
            "OPERATION": OperationRequest,
            "RULE": RuleRequest,
        }

        pydantic_class = model_mapping.get(template_type, TemplateMetaRequest)

        result = pydantic_mistakes(
            user_id=123,
            raw_request=raw_request,
            pydantic_class=pydantic_class,
            pydantic_class_name="template",
        )

        if isinstance(result, TemplateMetaRequest):
            return result

        elif isinstance(result, list) and all(isinstance(err, CommonMistake) for err in result):
            for mistake in result:
                self._mistake_service.create_mistake(mistake, user_id)

            raise ValueError("Handle template: syntax mistakes")

        raise TypeError("Handle template: unexpected result")

    def handle_lexic_mistakes(
        self,
        user_id: int,
        template: TemplateMetaRequest,
        resource: ResourceTypeRequest,
    ) -> None:
        try:
            object_reference = self._task_service.get_object_reference(
                resource.name,
                ResourceTypeRequest,
            )

            object_resource_type_reference = self._object_resource_type_service.get_object_reference(
                resource.rta_id,
                ResourceTypeRequest,
            )

        except ValueError:  # NotFoundError
            return

        mistakes = self._resource_name_lexic_mistakes(
            template,
            object_reference,
        )

        if len(mistakes) != 0:
            for mistake in mistakes:
                self._mistake_service.create_mistake(mistake, user_id)

            raise ValueError("Handle template: lexic mistakes")

    def handle_logic_mistakes(
        self,
        user_id: int,
        template: TemplateMetaRequest,
    ) -> None:
        try:
            object_reference = self._task_service.get_object_reference(
                template.name,
                TemplateMetaRequest,
            )

        except ValueError:  # NotFoundError
            return

        mistakes = self._rel_resources_logic_mistakes(
            template.rel_resources,
            object_reference.rel_resources,
        )

        if template.type == "IRREGULAR_EVENT":
            mistakes += self._irregular_event_logic_mistakes(template)

        elif template.type == "OPERATION":
            mistakes += self._operation_logic_mistakes(template)

        if len(mistakes) != 0:
            for mistake in mistakes:
                self._mistake_service.create_mistake(mistake, user_id)

            raise ValueError("Handle template: logic mistakes")

    def _rel_resources_logic_mistakes(
        self,
        rel_resources: List[RelevantResourceRequest],
        rel_resources_reference: List[RelevantResourceRequest],
    ) -> List[CommonMistake]:
        mistakes: List[CommonMistake] = []
        match_attrs_count = 0

        if id_template != id_template_reference:
            mistake = CommonMistake(
                message=f"Wrong template provided.",
            )
            mistakes.append(mistake)
            return mistakes

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
        attrs: List[TemplateMetaRequest],
        attrs_reference: List[TemplateMetaRequest],
    ) -> List[CommonMistake]:
        ...

    def _resource_name_lexic_mistakes(
        self,
        rel_resources: List[RelevantResourceRequest],
        reference: ResourceTypeRequest,
    ) -> List[CommonMistake]:
        mistakes = []
        for attr in attrs:
            find_flag = False
            closest_match = None
            for attr_reference in attrs_reference:
                if attr.name == attr_reference.name:
                    find_flag = True
                    break
                else:
                    distance = self._levenshtein_distance(attr.name, attr_reference.name)
                    if distance == 1:
                        closest_match = attr_reference.name
                        mistake = CommonMistake(
                            message=f"Attribute naming error.",
                        )
                        mistakes.append(mistake)
                        break

        return mistakes

    @staticmethod
    def _levenshtein_distance(s1: str, s2: str) -> int:
        if len(s1) < len(s2):
            return TemplateService._levenshtein_distance(s2, s1)

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
