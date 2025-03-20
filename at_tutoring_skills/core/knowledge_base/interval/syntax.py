from typing import TYPE_CHECKING

from at_krl.core.temporal.allen_interval import KBInterval
from rest_framework import exceptions

from at_tutoring_skills.core.data_serializers import KBIntervalDataSerializer
from at_tutoring_skills.core.knowledge_base.errors import to_syntax_mistake
from at_tutoring_skills.core.errors.models import CommonMistake

if TYPE_CHECKING:
    from at_tutoring_skills.core.knowledge_base.interval.service import KBIntervalService


class KBIntervalServiceSyntax:
    def process_tip(self, exception: str) -> str:
        ...

    async def handle_syntax_mistakes(self: "KBIntervalService", user_id: int, data: dict) -> KBInterval:
        serializer = KBIntervalDataSerializer(data=data["result"])
        try:
            await serializer.ais_valid(raise_exception=True)
            return await serializer.asave()
        except exceptions.ValidationError as e:
            syntax_mistakes: list[CommonMistake] = []
            for exception in e.detail:
                syntax_mistakes.append(
                    to_syntax_mistake(
                        user_id,
                        None,
                        self.process_tip(exception),
                    )
                )

            for syntax_mistake in syntax_mistakes:
                self.repository.create_mistake(syntax_mistake)

            raise e
