import asyncio
from typing import Dict, List

from at_tutoring_skills.apps.skills.models import SUBJECT_CHOICES
from at_tutoring_skills.core.errors.models import CommonMistake
from at_tutoring_skills.core.task.service import TaskService
from at_tutoring_skills.core.service.simulation.utils.utils import pydantic_mistakes
from at_tutoring_skills.core.errors.consts import SIMULATION_COEFFICIENTS
from at_tutoring_skills.core.errors.conversions import to_logic_mistake
from at_tutoring_skills.core.service.simulation.subservice.template_usage.models.models import (
    TemplateUsageArgumentRequest,
    TemplateUsageRequest,
)


class TemplateUsageService:
    def __init__(self, mistake_service, task_service):
        self._mistake_service = mistake_service
        self._task_service = task_service
        self.main_task_service = TaskService()

    async def handle_syntax_mistakes(self, user_id: int, data: dict) -> TemplateUsageRequest:
        """
        Обрабатывает синтаксические ошибки в данных шаблона.
        """
        raw_request = data.get("args", {}).get("templateUsage") or data.get("result")

        if raw_request is None:
            raise ValueError("Handle template usage: missing 'template' in input data")

        result = pydantic_mistakes(
            user_id=user_id,
            raw_request=raw_request,
            pydantic_class=TemplateUsageRequest,
            pydantic_class_name="template_usage",
        )
        print("Данные, полученные pydantic моделью: ", result)

        if isinstance(result, TemplateUsageRequest):
            return result
        elif isinstance(result, list) and all(isinstance(err, CommonMistake) for err in result):
            for mistake in result:
                await self.main_task_service.append_mistake(mistake)
                self._mistake_service.create_mistake(mistake, user_id, "syntax")
            raise ValueError("Handle template usage: syntax mistakes")
        raise TypeError("Handle template usage: unexpected result")

    async def handle_logic_mistakes(
        self,
        user_id: int,
        template_usage: TemplateUsageRequest,
        resource_reference: List[str],
        template_reference: str,
    ) -> None:
        """
        Обрабатывает логические ошибки в данных шаблона.
        """
        try:
            task = await self.main_task_service.get_task_by_name(
                template_usage.name, SUBJECT_CHOICES.SIMULATION_TEMPLATE_USAGES
            )
            task_id = task.pk
            object_reference = await self.main_task_service.get_template_usage_reference(task)
            print("Данные object reference, полученные для сравнения: ", object_reference)
        except ValueError:  # NotFoundError
            print("Создан образец операции, не касающийся задания")
            return

        mistakes: List[CommonMistake] = []

        mistakes.extend(
            self._template_logic_mistakes(
                user_id=user_id,
                template_usage=template_usage,
                template_reference=template_reference,
            )
        )

        mistakes.extend(
            self._arguments_logic_mistakes(
                user_id=user_id,
                arguments=template_usage.arguments,
                resource_reference=resource_reference,
            )
        )

        # Сохранение ошибок
        for mistake in mistakes:
            await self.main_task_service.append_mistake(mistake)
            self._mistake_service.create_mistake(mistake, user_id, "logic")

        if mistakes:
            raise ValueError("Handle template usage: logic mistakes")

    async def handle_lexic_mistakes(
        self,
        user_id: int,
        template_usage: TemplateUsageRequest,
        reference_template_usage: TemplateUsageRequest,
    ) -> None: ...

    def _template_logic_mistakes(
        self,
        user_id: int,
        template_usage: TemplateUsageRequest,
        template_reference: str,
    ) -> List[CommonMistake]:
        """
        Проверяет логические ошибки в основном шаблоне.
        """
        mistakes: List[CommonMistake] = []

        # Проверка template_id_str
        if template_usage.template_id_str != template_reference:
            mistake = to_logic_mistake(
                user_id=user_id,
                task_id=None,
                tip=f"Неверное значение образца операции. Ожидалось: {template_reference}.",
                coefficients=SIMULATION_COEFFICIENTS,
                entity_type="template_usage",
            )
            mistakes.append(mistake)

        return mistakes


    def _arguments_logic_mistakes(
            self,
            user_id: int,
            arguments: List[TemplateUsageArgumentRequest],
            resource_reference: List[str],  # Список строк
    ) -> List[CommonMistake]:
        """
        Проверяет логические ошибки в аргументах шаблона.
        """
        mistakes: List[CommonMistake] = []

        if not resource_reference:
            raise ValueError("Параметр resource_reference не должен быть пустым.")

        print(f"Reference names: {resource_reference}")

        for arg in arguments:
            print(f"\nProcessing argument: relevant_resource_id={arg.relevant_resource_id}, resource_id_str={arg.resource_id_str}")

            if arg.relevant_resource_id not in resource_reference:
                print(f"No reference found for relevant_resource_id={arg.relevant_resource_id}")
                mistake = to_logic_mistake(
                    user_id=user_id,
                    task_id=None,
                    tip=f"Ресурс с идентификатором {arg.relevant_resource_id} отсутствует в списке допустимых ресурсов.",
                    coefficients=SIMULATION_COEFFICIENTS,
                    entity_type="template_usage_argument",
                )
                mistakes.append(mistake)
                continue

            print(f"Found reference for relevant_resource_id={arg.relevant_resource_id}")

        return mistakes