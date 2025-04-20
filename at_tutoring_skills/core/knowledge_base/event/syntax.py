from typing import TYPE_CHECKING

from rest_framework import exceptions

from at_tutoring_skills.core.data_serializers import KBEventDataSerializer
from at_tutoring_skills.core.errors.conversions import to_syntax_mistake
from at_tutoring_skills.core.errors.models import CommonMistake
from at_tutoring_skills.core.task.service import TaskService


if TYPE_CHECKING:
    from at_tutoring_skills.core.knowledge_base.event.service import KBEventService
    from at_krl.core.temporal.allen_event import KBEvent


class KBEventServiceSyntax:
    async def handle_syntax_mistakes(self: "KBEventService", user_id: int, data: dict) -> "KBEvent":
        serializer = KBEventDataSerializer(data=data["result"])
        try:
            await serializer.ais_valid(raise_exception=True)
            return await serializer.asave()
        except exceptions.ValidationError as e:
            syntax_mistakes: list[CommonMistake] = []
            for exception in e.detail:
                syntax_mistakes.append(
                    to_syntax_mistake(
                        user_id,
                        tip=None,
                        coefficients=1,
                        entity_type=2,
                    )
                )

            for syntax_mistake in syntax_mistakes:
                task_servise = TaskService()
                task_servise.append_mistake(syntax_mistake)

            raise e
