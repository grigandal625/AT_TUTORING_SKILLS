from typing import TYPE_CHECKING

from at_krl.core.kb_rule import KBRule

from at_tutoring_skills.core.data_serializers import KBClassDataSerializer
from at_tutoring_skills.core.knowledge_base.errors import to_logic_mistake
from at_tutoring_skills.core.errors.models import CommonMistake

if TYPE_CHECKING:
    from at_tutoring_skills.core.knowledge_base.rule.service import KBRuleService


class KBRuleServiceLogicLexic:
    def process_tip(self, exception: str) -> str:
        ...

    def handle_logic_lexic_mistakes(self: "KBRuleService", user_id: int, data: dict) -> KBRule:
        ...
        # serializer = KBClassDataSerializer(data=data["args"])
        # try:
        #     serializer.IsValid(raise_exception=True)
        #     return serializer.Save()
        # except BaseException as e:
        #     syntax_mistakes: list[CommonMistake] = []
        #     for exception in e.detail:
        #         syntax_mistakes.append(
        #             to_logic_mistake(
        #                 user_id,
        #                 None,
        #                 self.process_tip(exception),
        #             )
        #         )

        #     for syntax_mistake in syntax_mistakes:
        #         self.repository.create_mistake(syntax_mistake)

        #     raise e
