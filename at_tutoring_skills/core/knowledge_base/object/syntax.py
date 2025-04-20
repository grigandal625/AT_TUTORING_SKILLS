from typing import TYPE_CHECKING

from at_krl.core.kb_class import KBClass
from at_krl.utils.context import Context
from rest_framework import exceptions

from at_tutoring_skills.core.data_serializers import KBClassDataSerializer
from at_tutoring_skills.core.errors.consts import KNOWLEDGE_COEFFICIENTS
from at_tutoring_skills.core.errors.conversions import to_syntax_mistake
from at_tutoring_skills.core.errors.models import CommonMistake
from at_tutoring_skills.core.task.service import KBTypeRootModel
from at_tutoring_skills.core.task.service import TaskService


if TYPE_CHECKING:
    from at_tutoring_skills.core.knowledge_base.object.service import KBObjectService
    from at_krl.core.kb_type import KBType
    from at_queue.core.at_component import ATComponent


class KBObjectServiceSyntax:  # Изменено
    component: "ATComponent"

    def __init__(self, component: "ATComponent"):
        self.component = component

    async def handle_syntax_mistakes(
        self: "KBObjectService", user_id: int, data: dict
    ) -> KBClass:  # Изменено аннотация типа
        async def get_type_by_id(type_id: int) -> "KBType":
            type_data = await self.component.exec_external_method("ATKRLEditor", "get_type", {"id": type_id})
            model = KBTypeRootModel(root=type_data)
            return model.to_internal(context=Context(name="getter"))

        serializer = KBClassDataSerializer(data=data["result"], context={"type_by_id_getter": get_type_by_id})
        try:
            await serializer.ais_valid(raise_exception=True)
            return await serializer.asave()
        except exceptions.ValidationError as e:
            syntax_mistakes: list[CommonMistake] = []
            for exception in e.detail:
                syntax_mistakes.append(
                    to_syntax_mistake(user_id, tip=self.process_tip(exception), coefficients=KNOWLEDGE_COEFFICIENTS, entity_type="object")
                )

            for syntax_mistake in syntax_mistakes:
                task_service = TaskService()
                task_service.append_mistake(syntax_mistake)

            raise e

    def process_tip(self, exception: str) -> str:
        ...
        return str(exception)
