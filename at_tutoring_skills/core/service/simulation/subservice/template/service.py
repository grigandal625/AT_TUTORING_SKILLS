



class TemplateService:
    ...


# def __init__(
#     self,
#     mistake_service: IMistakeService,
#     task_service: ITaskService,
#     object_resource_type_service: IResourceTypeComponent,
# ):
#     self._mistake_service = mistake_service
#     self._task_service = task_service
#     self._object_resource_type_service = object_resource_type_service

# def handle_syntax_mistakes(
#     self,
#     user_id: int,
#     raw_request: dict,
# ) -> TemplateMetaRequest:
#     template_type = raw_request.get("type")

#     model_mapping: dict[str, Type[BaseModel]] = {
#         "IRREGULAR_EVENT": IrregularEventRequest,
#         "OPERATION": OperationRequest,
#         "RULE": RuleRequest,
#     }

#     pydantic_class = model_mapping.get(template_type, TemplateMetaRequest)

#     result = pydantic_mistakes(
#         user_id=123,
#         raw_request=raw_request,
#         pydantic_class=pydantic_class,
#         pydantic_class_name="template",
#     )

#     if isinstance(result, TemplateMetaRequest):
#         return result

#     elif isinstance(result, list) and all(
#         isinstance(err, CommonMistake) for err in result
#     ):
#         for mistake in result:
#             self._mistake_service.create_mistake(mistake, user_id)

#         raise ValueError("Handle template: syntax mistakes")

#     raise TypeError("Handle template: unexpected result")

# def handle_lexic_mistakes(
#     self,
#     user_id: int,
#     template: TemplateMetaRequest
# ) -> None:
#     try:
#         object_reference = self._task_service.get_object_reference(
#             template.name,
#             TemplateMetaRequest,
#         )

#     except ValueError:  # NotFoundError
#         return

#     mistakes = self._rel_resource_name_lexic_mistakes(
#         template,
#         object_reference
#     )

#     if len(mistakes) != 0:
#         for mistake in mistakes:
#             self._mistake_service.create_mistake(mistake, user_id)

#         raise ValueError("Handle template: lexic mistakes")

# def handle_logic_mistakes(
#     self,
#     user_id: int,
#     template: TemplateMetaRequest,
# ) -> None:
#     try:
#         object_reference = self._task_service.get_object_reference(
#             template.name,
#             TemplateMetaRequest,
#         )

#     except ValueError:  # NotFoundError
#         return

#     mistakes = self._rel_resources_logic_mistakes(
#         template.rel_resources,
#         object_reference.rel_resources,
#     )


#     if template.type == "IRREGULAR_EVENT":
#         object_reference = self._task_service.get_object_reference(
#             template.name,
#             IrregularEventGenerator,
#         )

#         mistakes += self._irregular_event_logic_mistakes(
#             template.rel_resources,
#             object_reference.rel_resources,
#         )

#     elif template.type == "OPERATION":
#         object_reference = self._task_service.get_object_reference(
#             template.name,
#             OperationBody,
#         )

#         mistakes += self._operation_logic_mistakes(
#             template.rel_resources,
#             object_reference.rel_resources,
#         )


#     if len(mistakes) != 0:
#         for mistake in mistakes:
#             self._mistake_service.create_mistake(mistake, user_id)

#         raise ValueError("Handle template: logic mistakes")


# def _rel_resources_logic_mistakes(
#     self,
#     rel_resources: List[RelevantResourceRequest],
#     rel_resources_reference: List[RelevantResourceRequest]
# ) -> List[CommonMistake]:

#     mistakes: List[CommonMistake] = []
#     match_rel_resource_count = 0

#     resource_type = self._object_resource_type_service.get_object_reference(
#         rel_resources.resource_type_id,
#         ResourceTypeRequest,
#     )

#     for rel_resource in rel_resources:
#         find_flag = False
#         for rel_resource_reference in rel_resources_reference:
#             if rel_resource.name == rel_resource_reference.name:
#                 find_flag = True
#                 match_rel_resource_count += 1
#                 if resource_type.name != rel_resource_reference.name:
#                     mistake = CommonMistake(
#                         message=f"Invalid relevant resource type'{rel_resource.name}'.",
#                     )
#                     mistakes.append(mistake)
#                     continue

#         if not find_flag:
#             mistake = CommonMistake(
#                 message=f"Unknown attribute'{rel_resource.name}'.",
#             )
#             mistakes.append(mistake)

#     if match_rel_resource_count < len(rel_resources_reference):
#         mistake = CommonMistake(
#             message=f"Missing required attributes.",
#         )
#         mistakes.append(mistake)

#     return mistakes


# def _rel_resource_name_lexic_mistakes(
#     self,
#     rel_resources: List[RelevantResourceRequest],
#     rel_resources_reference: List[RelevantResourceRequest],
# ) -> List[CommonMistake]:

#     mistakes: List[CommonMistake] = []

#     for rel_resource in rel_resources:
#         find_flag = False
#         closest_match = None

#         for rel_resource_reference in rel_resources_reference:
#             if rel_resource.name == rel_resource_reference.name:
#                 find_flag = True
#                 break
#             else:
#                 distance = self._levenshtein_distance(rel_resource.name, rel_resource_reference.name)
#                 if distance == 1:
#                     closest_match = rel_resource_reference.name
#                     mistake = CommonMistake(
#                         message=f"Relevant resource naming error.",
#                     )
#                     mistakes.append(mistake)
#                     break

#     return mistakes

# @staticmethod
# def _levenshtein_distance(s1: str, s2: str) -> int:
#     if len(s1) < len(s2):
#         return TemplateService._levenshtein_distance(s2, s1)

#     if len(s2) == 0:
#         return len(s1)

#     previous_row = range(len(s2) + 1)
#     for i, c1 in enumerate(s1):
#         current_row = [i + 1]
#         for j, c2 in enumerate(s2):
#             insertions = previous_row[j + 1] + 1
#             deletions = current_row[j] + 1
#             substitutions = previous_row[j] + (c1 != c2)
#             current_row.append(min(insertions, deletions, substitutions))
#         previous_row = current_row

#     return previous_row[-1]
