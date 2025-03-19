from typing import List

from pydantic import ValidationError
from pydantic_core import ErrorDetails

from at_tutoring_skills.core.errors.consts import SIMULATION_COEFFICIENTS
from at_tutoring_skills.core.errors.conversions import to_syntax_mistake
from at_tutoring_skills.core.errors.models import CommonMistake
from at_tutoring_skills.core.service.simulation.subservice.template_usage.dependencies import (
    IMistakeService,
    ITaskService,
)
from at_tutoring_skills.core.service.simulation.subservice.template_usage.models.models import (
    TemplateUsageArgumentRequest,
    TemplateUsageRequest
)
from at_tutoring_skills.core.service.simulation.utils.utils import pydantic_mistakes


class TemplateUsageService:
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
    ) -> TemplateUsageRequest:
        result = pydantic_mistakes(
            user_id=123,
            raw_request=raw_request,
            pydantic_class=TemplateUsageRequest,
            pydantic_class_name="template_usage",
        )

        if isinstance(result, TemplateUsageRequest):
            return result

        elif isinstance(result, list) and all(
            isinstance(err, CommonMistake) for err in result
        ):
            for mistake in result:
                self._mistake_service.create_mistake(mistake, user_id)

            raise ValueError("Handle template usage: syntax mistakes")

        raise TypeError("Handle template usage type: unexpected result")

    def handle_logic_mistakes(
        self,
        user_id: int,
        template: TemplateUsageRequest,
    ) -> None: ...

    def handle_lexic_mistakes(
        self,
        user_id: int,
        template: TemplateUsageRequest,
    ) -> None: ...
