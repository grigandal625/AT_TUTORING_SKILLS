import json
from typing import List, Union

from jsonschema import ValidationError

from at_tutoring_skills.apps.skills.models import Task
from at_tutoring_skills.core.errors.models import CommonMistake

from at_tutoring_skills.apps.skills.models import SUBJECT_CHOICES
from at_tutoring_skills.core.errors.consts import SIMULATION_COEFFICIENTS

from at_tutoring_skills.core.errors.conversions import to_lexic_mistake
from at_tutoring_skills.core.errors.conversions import to_logic_mistake

from at_tutoring_skills.core.service.simulation.dependencies import ITaskService
from at_tutoring_skills.core.service.simulation.subservice.resource_type.dependencies import IMistakeService
from at_tutoring_skills.core.service.simulation.subservice.resource_type.models.models import ResourceTypeRequest
from at_tutoring_skills.core.service.simulation.subservice.template.models.models import IrregularEventRequest, OperationRequest, RelevantResourceRequest, RuleRequest, TemplateMetaRequest
from at_tutoring_skills.core.service.simulation.utils.utils import pydantic_mistakes
from at_tutoring_skills.core.task.service import TaskService


class TemplateService:
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
            data: dict
        ) -> Union[IrregularEventRequest, RuleRequest, OperationRequest]:
        template_type = data["args"]["template"]["meta"]["type"]
        pydantic_class = self._get_template_class(template_type)
        
        result = pydantic_mistakes(
            user_id=user_id,
            raw_request=data["args"]["template"],
            pydantic_class=pydantic_class,
            pydantic_class_name="template",
        )
        print("Данные, полученные pydantic моделью: ", result)

        if isinstance(result, (IrregularEventRequest, RuleRequest, OperationRequest)):
            return result
        elif isinstance(result, list) and all(isinstance(err, CommonMistake) for err in result):
            for mistake in result:
                await self.main_task_service.append_mistake(mistake)
                self._mistake_service.create_mistake(mistake, user_id, "syntax")
            raise ValueError("Handle template: syntax mistakes")
        raise TypeError("Handle template: unexpected result")


    async def handle_logic_mistakes(
        self,
        user_id: int,
        template: Union[IrregularEventRequest, RuleRequest, OperationRequest],
        resource_type: str,
    ) -> None:
        """
        Обработка логических ошибок.
        """
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
                template.meta.name, SUBJECT_CHOICES.SIMULATION_TEMPLATES
            )

            task_id = task.pk
            object_reference = await self.main_task_service.get_template_reference(task)
            print("Данные object reference, полученные для сравнения: ", object_reference)
        except ValueError:  # NotFoundError
            print("Создан шаблон, не касающийся задания")
            return

        mistakes = self._attributes_logic_mistakes(
            resource_type_obj,
            template,
            object_reference,
            user_id,
            task_id,
        )
        print("Найденные ошибки: ", mistakes)
        if len(mistakes) != 0:
            for mistake in mistakes:
                await self.main_task_service.append_mistake(mistake)
            return mistakes  # raise ValueError("Handle template: logic mistakes")


    async def handle_lexic_mistakes(
        self,
        user_id: int,
        template: Union[IrregularEventRequest, RuleRequest, OperationRequest],
    ) -> None:
        """
        Обработка лексических ошибок.
        """
        try:
            task: Task = await self.main_task_service.get_task_by_name(
                template.meta.name, SUBJECT_CHOICES.SIMULATION_TEMPLATES
            )
            task_id = task.pk
            object_reference = await self.main_task_service.get_template_reference(task)
            print("Данные object reference, полученные для сравнения: ", object_reference)
        except ValueError:  # NotFoundError
            return

        mistakes = self._attributes_lexic_mistakes(
            template.meta.rel_resources,
            object_reference.meta.rel_resources,
            user_id,
            task_id,
        )
        if len(mistakes) != 0:
            for mistake in mistakes:
                await self.main_task_service.append_mistake(mistake)
            return mistakes  # raise ValueError("Handle template: lexic mistakes")


    def _get_template_class(self, template_type: str):
        """
        Возвращает соответствующий класс Pydantic на основе типа шаблона.
        """
        type_to_class = {
            "IRREGULAR_EVENT": IrregularEventRequest,
            "RULE": RuleRequest,
            "OPERATION": OperationRequest,
        }
        return type_to_class.get(template_type)



    def _attributes_logic_mistakes(
        self,
        resource_type: ResourceTypeRequest,
        template: Union[IrregularEventRequest, RuleRequest, OperationRequest],
        template_reference: Union[IrregularEventRequest, RuleRequest, OperationRequest],
        user_id: int,
        task_id: int,
    ) -> List[CommonMistake]:
        """
        Проверка логических ошибок в шаблоне.
        """
        mistakes: List[CommonMistake] = []
        match_attrs_count = 0

        print(f"Reference resource type: {resource_type.name}")

        if template.meta.type != template_reference.meta.type:
            mistake = to_logic_mistake(
                user_id=user_id,
                task_id=task_id,
                tip=f"Указан неправильный тип шаблона.",
                coefficients=SIMULATION_COEFFICIENTS,
                entity_type="template",
            )
            mistakes.append(mistake)
            return mistakes

        # Сравнение связанных ресурсов
        rel_resources = template.meta.rel_resources
        rel_resources_reference = template_reference.meta.rel_resources
        attrs_reference_dict = {attr.name: attr for attr in attrs_reference}
       
        if len(rel_resources) != len(rel_resources_reference):
            mistake = to_logic_mistake(
                user_id=user_id,
                task_id=task_id,
                tip=f"Указано неправильное количество связанных ресурсов.",
                coefficients=SIMULATION_COEFFICIENTS,
                entity_type="template",
            )
            mistakes.append(mistake)

        # Создаем словарь для быстрого поиска эталонных ресурсов
        rel_resources_reference_dict = {res.name: res for res in rel_resources_reference}
        for res in rel_resources:
            if res.name not in rel_resources_reference_dict:
                continue

            res_reference = rel_resources_reference_dict[res.name]
            if res.resource_type_id != res_reference.resource_type_id:
                mistake = to_logic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip=f"Недопустимый resource_type_id для ресурса '{res.name}'.",
                    coefficients=SIMULATION_COEFFICIENTS,
                    entity_type="template",
                )
                mistakes.append(mistake)

        # Сравнение тела шаблона
        if isinstance(template, IrregularEventRequest):
            if template.generator.type != template_reference.generator.type:
                mistake = to_logic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip=f"Недопустимый тип генератора.",
                    coefficients=SIMULATION_COEFFICIENTS,
                    entity_type="template",
                )
                mistakes.append(mistake)

            if template.generator.value != template_reference.generator.value:
                mistake = to_logic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip=f"Неверное значение генератора.",
                    coefficients=SIMULATION_COEFFICIENTS,
                    entity_type="template",
                )
                mistakes.append(mistake)

            if template.generator.dispersion != template_reference.generator.dispersion:
                mistake = to_logic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip=f"Неверное значение дисперсии генератора.",
                    coefficients=SIMULATION_COEFFICIENTS,
                    entity_type="template",
                )
                mistakes.append(mistake)

        if template.body != template_reference.body:
            mistake = to_logic_mistake(
                user_id=user_id,
                task_id=task_id,
                tip=f"Неверное тело шаблона.",
                coefficients=SIMULATION_COEFFICIENTS,
                entity_type="template",
            )
            mistakes.append(mistake)

        return mistakes

    def _attributes_lexic_mistakes(
        self,
        rel_resources: List[RelevantResourceRequest],
        rel_resources_reference: List[RelevantResourceRequest],
        user_id: int,
        task_id: int,
    ) -> List[CommonMistake]:
        """
        Проверка лексических ошибок в связанных ресурсах.
        """
        mistakes = []
        rel_resources_reference_dict = {res.name: res for res in rel_resources_reference}

        for res in rel_resources:
            if res.name in rel_resources_reference_dict:
                continue

            closest_match = None
            min_distance = float("inf")
            for res_reference in rel_resources_reference:
                distance = self._levenshtein_distance(res.name, res_reference.name)
                if distance < min_distance:
                    min_distance = distance
                    closest_match = res_reference.name

            if closest_match and min_distance <= 1:
                mistake = to_lexic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip=f"Ошибка в имени ресурса: {res.name} не найден, но {closest_match} является ближайшим.",
                    coefficients=SIMULATION_COEFFICIENTS,
                    entity_type="template",
                )
                mistakes.append(mistake)
            else:
                mistake = to_lexic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip=f"Неизвестный ресурс: {res.name} не найден.",
                    coefficients=SIMULATION_COEFFICIENTS,
                    entity_type="template",
                )
                mistakes.append(mistake)

        return mistakes

    @staticmethod
    def _levenshtein_distance(s1: str, s2: str) -> int:
        """
        Вычисление расстояния Левенштейна между двумя строками.
        """
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