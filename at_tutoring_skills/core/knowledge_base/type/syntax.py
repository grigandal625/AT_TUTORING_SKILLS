from typing import TYPE_CHECKING

from at_krl.core.kb_type import KBType
from rest_framework import exceptions

from at_tutoring_skills.core.data_serializers import KBTypeDataSerializer
from at_tutoring_skills.core.knowledge_base.errors import to_syntax_mistake
from at_tutoring_skills.core.models.models import CommonMistake

if TYPE_CHECKING:
    from at_tutoring_skills.core.knowledge_base.type.service import KBTypeService


class KBTypeServiceSyntax:
    async def handle_syntax_mistakes(self: "KBTypeService", user_id: int, data: dict) -> KBType:
        serializer = KBTypeDataSerializer(data=data["result"])
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

    def process_tip(exception: str) -> str:
        ...
