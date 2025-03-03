from at_krl.core.kb_type import KBType

from at_tutoring_skills.core.knowledge_base.type.errors import to_syntax_mistake
from at_tutoring_skills.core.knowledge_base.type.service import KBTypeService
from at_tutoring_skills.core.models.models import CommonMistake


def handle_syntax_mistakes(service: KBTypeService, user_id: int, data: dict) -> KBType:
    serializer = KBTypeSerializer(data=data["args"])
    try:
        serializer.IsValid(raise_exception=True)
        return serializer.Save()
    except BaseException as e:
        syntax_mistakes: list[CommonMistake] = []
        for exception in e.detail:
            syntax_mistakes.append(
                to_syntax_mistake(
                    user_id,
                    None,
                    process_tip(exception),
                )
            )

        for syntax_mistake in syntax_mistakes:
            service.repository.create_mistake(syntax_mistake)

        raise e


def process_tip(exception: str) -> str: ...

