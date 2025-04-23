from typing import Dict
from typing import List
from typing import Union

from at_tutoring_skills.apps.skills.models import SUBJECT_CHOICES
from at_tutoring_skills.apps.skills.models import Task
from at_tutoring_skills.core.errors.consts import SIMULATION_COEFFICIENTS
from at_tutoring_skills.core.errors.conversions import to_lexic_mistake, to_syntax_mistake
from at_tutoring_skills.core.errors.conversions import to_logic_mistake
from at_tutoring_skills.core.errors.models import CommonMistake
from at_tutoring_skills.core.service.simulation.dependencies import ITaskService
from at_tutoring_skills.core.service.simulation.subservice.resource_type.dependencies import IMistakeService
from at_tutoring_skills.core.service.simulation.subservice.template.models.models import IrregularEventRequest
from at_tutoring_skills.core.service.simulation.subservice.template.models.models import OperationRequest
from at_tutoring_skills.core.service.simulation.subservice.template.models.models import RelevantResourceRequest
from at_tutoring_skills.core.service.simulation.subservice.template.models.models import RuleRequest
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

    def _get_template_class(self, template_type: str):
        type_to_class = {
            "IRREGULAR_EVENT": IrregularEventRequest,
            "RULE": RuleRequest,
            "OPERATION": OperationRequest,
        }
        return type_to_class.get(template_type)

    async def handle_syntax_mistakes(
        self, user_id: int, data: dict
    ) -> Union[IrregularEventRequest, RuleRequest, OperationRequest]:
        template_type = data["args"]["template"]["meta"]["type"]
        pydantic_class = self._get_template_class(template_type)

        result = pydantic_mistakes(
            user_id=user_id,
            raw_request=data["args"]["template"],
            pydantic_class=pydantic_class,
            pydantic_class_name="template",
        )
        errors_list = []

        print("Данные, полученные pydentic моделью: ", result)

        if isinstance(result, (IrregularEventRequest, RuleRequest, OperationRequest)):
            return result
        elif isinstance(result, list) and all(isinstance(err, CommonMistake) for err in result):
            for mistake in result:
                # await self.main_task_service.append_mistake(mistake)
                # self._mistake_service.create_mistake(mistake, user_id, "syntax")

                common_mistake = to_syntax_mistake(
                        user_id=user_id,
                        tip=f"Синтаксическая ошибка при создании образца операции.\n\n",
                        coefficients=SIMULATION_COEFFICIENTS,
                        entity_type="template",
                        skills=[270],

                )
                errors_list.append(common_mistake)
                await self.main_task_service.append_mistake(common_mistake)

            raise ValueError("Синтаксическая ошибка при создании образца операции")


    async def handle_logic_mistakes(
        self,
        user_id: int,
        template: Union[IrregularEventRequest, RuleRequest, OperationRequest],
        resource_data: List[Dict[str, str]],
    ) -> None:
        try:
            task: Task = await self.main_task_service.get_task_by_name(
                template.meta.name, SUBJECT_CHOICES.SIMULATION_TEMPLATES
            )
            task_id = task.pk
            object_reference = await self.main_task_service.get_template_reference(task)

            print("Данные object reference, полученные для сравнения: ", object_reference)

        except ValueError:  # NotFoundError
            print("Создан образец операции, не касающийся задания")
            return

        mistakes: List[CommonMistake] = []

        if isinstance(template, (IrregularEventRequest, RuleRequest, OperationRequest)):
            # Проверяем, что object_reference имеет тот же тип, что и template
            if not isinstance(object_reference, type(template)):
                mistake = to_logic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip=f"Выбран неверный вид образца операции. Ожидался тип {type(template).__name__}, "
                        f"но получен тип {type(object_reference).__name__}.\n\n",
                    coefficients=SIMULATION_COEFFICIENTS,
                    entity_type="template",
                    skills=[241],
                )
                mistakes.append(mistake)
                return mistakes

        mistake = self._relevant_resources_logic_mistakes(
            resource_data,
            template,
            object_reference.meta.rel_resources,
            user_id,
            task_id,
        )
        if mistake:  # Добавляем только непустые ошибки
            mistakes.extend(mistake)

        if isinstance(template, IrregularEventRequest):
            mistake = self._generator_logic_mistakes(
                template,
                object_reference,
                user_id,
                task_id,
            )

            if mistake:  # Добавляем только непустые ошибки
                mistakes.extend(mistake)

        mistake = self._body_logic_mistakes(
            template,
            object_reference,
            user_id,
            task_id,
        )

        if mistake:  # Добавляем только непустые ошибки
            mistakes.extend(mistake)

        print("Найденные ошибки: ", mistakes)

        if len(mistakes) != 0:
            for mistake in mistakes:
                await self.main_task_service.append_mistake(mistake)

            return mistakes  # raise ValueError("Handle template: logic mistakes")

    async def handle_lexic_mistakes(
        self,
        user_id: int,
        template: Union[IrregularEventRequest, RuleRequest, OperationRequest],
        resource_data: List[Dict[str, str]],
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
            print("Создан образец операции, не касающийся задания")
            return
        
        if isinstance(template, (IrregularEventRequest, RuleRequest, OperationRequest)):
            # Проверяем, что object_reference имеет тот же тип, что и template
            if not isinstance(object_reference, type(template)):
                return 
        
        mistakes = self._relevant_resources_lexic_mistakes(
            resource_data,
            template,
            object_reference.meta.rel_resources,
            user_id,
            task_id,
        )

        print("Найденные ошибки: ", mistakes)

        if len(mistakes) != 0:
            for mistake in mistakes:
                await self.main_task_service.append_mistake(mistake)

            return mistakes  # raise ValueError("Handle template: lexic mistakes")

    def _relevant_resources_logic_mistakes(
        self,
        resource_data: List[Dict[str, str]],
        template: Union[IrregularEventRequest, RuleRequest, OperationRequest],
        rel_resources_reference: List[RelevantResourceRequest],
        user_id: int,
        task_id: int,
    ) -> List[CommonMistake]:
        """
        Проверка логических ошибок в релевантных ресурсах
        """
        mistakes: List[CommonMistake] = []
        match_attrs_count = 0

        rel_resources = resource_data  # Список словарей
        reference_dict = {res.name: res for res in rel_resources_reference}

        if resource_data is None:
            mistake = to_logic_mistake(
                user_id=user_id,
                task_id=task_id,
                tip="Данные релевантных ресурсов не были загружены.\n\n",
                coefficients=SIMULATION_COEFFICIENTS,
                entity_type="template",
                skills=[242],
            )
            mistakes.append(mistake)
            return mistakes

        if len(rel_resources) != len(rel_resources_reference):
            mistake = to_logic_mistake(
                user_id=user_id,
                task_id=task_id,
                tip=f"Указано неправильное количество связанных ресурсов.\n\n",
                coefficients=SIMULATION_COEFFICIENTS,
                entity_type="template",
                skills=[242],
            )
            mistakes.append(mistake)
            return mistakes

        # resource - полученные данные
        for resource in rel_resources:
            resource_name = resource.get("name")
            resource_type = resource.get("resource_type_str")

            for resource_reference in rel_resources_reference:
                resource_name_reference = resource_reference.name
                resource_type_reference = resource_reference.resource_type_id_str

                if resource_name not in reference_dict:
                    mistake = to_logic_mistake(
                        user_id=user_id,
                        task_id=task_id,
                        tip=f"Введено имя релевантного ресурса {resource_name} не касающийся данного образца операции.\n\n",
                        coefficients=SIMULATION_COEFFICIENTS,
                        entity_type="template",
                        skills=[242],
                    )
                    mistakes.append(mistake)
                    continue

                if resource_name == resource_name_reference:
                    # Сравниваем типы ресурсов
                    if str(resource_type) != str(resource_type_reference):  # Преобразуем оба значения в строки
                        mistake = to_logic_mistake(
                            user_id=user_id,
                            task_id=task_id,
                            tip=f"Тип ресурса {resource_name} не совпадает с эталонным типом (ожидалось: {resource_type_reference}).\n\n",
                            coefficients=SIMULATION_COEFFICIENTS,
                            entity_type="template",
                            skills=[242],
                        )
                        mistakes.append(mistake)

        return mistakes

    def _generator_logic_mistakes(
        self,
        template: IrregularEventRequest,
        template_reference: IrregularEventRequest,
        user_id: int,
        task_id: int,
    ) -> List[CommonMistake]:
        mistakes: List[CommonMistake] = []
        match_attrs_count = 0

        generator = template.generator
        generator_reference = template_reference.generator

        if generator.type != generator_reference.type:
            mistake = to_logic_mistake(
                user_id=user_id,
                task_id=task_id,
                tip=f"Тип генератора {generator.type} не соответствует эталонному типу.\n\n",
                coefficients=SIMULATION_COEFFICIENTS,
                entity_type="template",
                skills=[243],
            )
            mistakes.append(mistake)

        if generator.value != generator_reference.value:
            mistake = to_logic_mistake(
                user_id=user_id,
                task_id=task_id,
                tip=f"Значение генератора {generator.value} не соответствует эталонному значению.\n\n",
                coefficients=SIMULATION_COEFFICIENTS,
                entity_type="template",
                skills=[243],
            )
            mistakes.append(mistake)

        if generator.dispersion != generator_reference.dispersion:
            mistake = to_logic_mistake(
                user_id=user_id,
                task_id=task_id,
                tip=f"Дисперсия генератора {generator.dispersion} не соответствует эталонной дисперсии.\n\n",
                coefficients=SIMULATION_COEFFICIENTS,
                entity_type="template",
                skills=[243],
            )
            mistakes.append(mistake)

        return mistakes

    def _body_logic_mistakes(
        self,
        template: Union[IrregularEventRequest, RuleRequest, OperationRequest],
        template_reference: Union[IrregularEventRequest, RuleRequest, OperationRequest],
        user_id: int,
        task_id: int,
    ) -> List[CommonMistake]:
        """
        Проверка логических ошибок
        """
        mistakes: List[CommonMistake] = []
        match_attrs_count = 0

        # Для IrregularEventRequest
        if isinstance(template, IrregularEventRequest):
            if not template.body.body.strip():
                mistake = to_logic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip="Тело в образце операций пустое.\n\n",
                    coefficients=SIMULATION_COEFFICIENTS,
                    entity_type="template",
                    skills=[243],
                )
                mistakes.append(mistake)

        # Для RuleRequest
        elif isinstance(template, RuleRequest):
            if not template.body.condition.strip():
                mistake = to_logic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip="Условие в образце операций пустое.\n\n",
                    coefficients=SIMULATION_COEFFICIENTS,
                    entity_type="template",
                    skills=[243, 245, 246],
                )
                mistakes.append(mistake)

            if not template.body.body.strip():
                mistake = to_logic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip="Тело в образце операций пустое.\n\n",
                    coefficients=SIMULATION_COEFFICIENTS,
                    entity_type="template",
                    skills=[243, 245, 246],
                )
                mistakes.append(mistake)

        # Для OperationRequest
        elif isinstance(template, OperationRequest):
            if not template.body.condition.strip():
                mistake = to_logic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip="Условие в образце операций пустое.\n\n",
                    coefficients=SIMULATION_COEFFICIENTS,
                    entity_type="template",
                    skills=[243, 245, 246],
                )
                mistakes.append(mistake)

            if template.body.delay != template_reference.body.delay:
                mistake = to_logic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip="неправильное указание длительности в образце перации.\n\n",
                    coefficients=SIMULATION_COEFFICIENTS,
                    entity_type="template",
                    skills=[245],
                )
                mistakes.append(mistake)

            if not template.body.body_before.strip():
                mistake = to_logic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip="Тело body_before в образце операций пустое.\n\n",
                    coefficients=SIMULATION_COEFFICIENTS,
                    entity_type="template",
                    skills=[245, 246],
                )
                mistakes.append(mistake)

            if not template.body.body_after.strip():
                mistake = to_logic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip="Тело body_after в образце операций пустое.\n\n",
                    coefficients=SIMULATION_COEFFICIENTS,
                    entity_type="template",
                    skills=[245, 246],
                )
                mistakes.append(mistake)

        return mistakes

    def _relevant_resources_lexic_mistakes(
        self,
        resource_data: List[Dict[str, str]],
        template: Union[IrregularEventRequest, RuleRequest, OperationRequest],
        rel_resources_reference: List[RelevantResourceRequest],
        user_id: int,
        task_id: int,
    ) -> List[CommonMistake]:
        """
        Проверка лексических ошибок в релевантных ресурсах
        """
        mistakes: List[CommonMistake] = []
        match_attrs_count = 0

        rel_resources = resource_data  # Список словарей
        reference_dict = {res.name: res for res in rel_resources_reference}

        for resource in rel_resources:
            resource_name = resource.get("name")

            if resource_name in reference_dict:
                continue

            closest_match = None
            min_distance = float("inf")
            for resource_reference in rel_resources_reference:
                distance = self._levenshtein_distance(resource_name, resource_reference.name)
                if distance < min_distance:
                    min_distance = distance
                    closest_match = resource_reference.name

            if closest_match and min_distance <= 1:
                mistake = to_lexic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip=f"Ошибка в имени ресурса: '{resource_name}' не найден, но '{closest_match}' является ближайшим.\n\n",
                    coefficients=SIMULATION_COEFFICIENTS,
                    entity_type="template",
                    skills=[242],
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
