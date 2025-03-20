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


# class TemplateUsageService:
#     def __init__(
#         self,
#         mistake_service: IMistakeService,
#         task_service: ITaskService,
#     ):
#         self._mistake_service = mistake_service
#         self._task_service = task_service

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
    
