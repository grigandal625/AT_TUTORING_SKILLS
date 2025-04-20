from typing import TYPE_CHECKING

from at_krl.core.kb_rule import KBRule
from rest_framework import exceptions

from at_tutoring_skills.core.data_serializers import KBRuleDataSerializer
from at_tutoring_skills.core.errors.conversions import to_syntax_mistake
from at_tutoring_skills.core.errors.models import CommonMistake
from at_tutoring_skills.core.task.service import TaskService

if TYPE_CHECKING:
    from at_tutoring_skills.core.knowledge_base.rule.service import KBRuleService


class KBRuleServiceSyntax:
    async def handle_syntax_mistakes(self: "KBRuleService", user_id: int, data: dict) -> KBRule:
        serializer = KBRuleDataSerializer(data=data["result"])
        try:
            await serializer.ais_valid(raise_exception=True)
            return await serializer.asave()
        except exceptions.ValidationError as e:
            syntax_mistakes: list[CommonMistake] = []
            for exception in e.detail:
                syntax_mistakes.append(
                    to_syntax_mistake(user_id, tip=self.process_tip(exception), coefficients=0.5, entity_type="rule")
                )

            for syntax_mistake in syntax_mistakes:
                task_servise = TaskService()
                task_servise.append_mistake(syntax_mistake)

            raise e

    def process_tip(exception: str) -> str:
        ...
        return str(exception)
