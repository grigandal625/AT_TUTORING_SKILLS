from typing import TYPE_CHECKING

from at_krl.core.temporal.allen_event import KBEvent

from at_tutoring_skills.core.data_serializers import KBEventDataSerializer
from at_tutoring_skills.core.errors.context import Context 
from at_tutoring_skills.core.errors.conversions import to_logic_mistake
from at_tutoring_skills.core.errors.models import CommonMistake

if TYPE_CHECKING:
    from at_tutoring_skills.core.knowledge_base.event.service import KBEventService


class KBEventServiceLogicLexic:
    def estimate_event(self, etalon_event: dict, event: KBEvent, context: Context):
        print("Estimate event")

        event_et = KBEvent.from_dict(etalon_event)
        if event_et.id == event.id:
            self.estimate_condition(
                event_et.occurance_condition, event.occurance_condition, context=context.create_child("open condition")
            )

    def process_tip(self, exception: str) -> str:
        ...

    def handle_logic_lexic_mistakes(self, service: KBEventService, user_id: int, data: dict) -> KBEvent:
        serializer = KBEventDataSerializer(data=data["args"])
        try:
            serializer.IsValid(raise_exception=True)
            return serializer.Save()
        except BaseException as e:
            syntax_mistakes: list[CommonMistake] = []
            for exception in e.detail:
                syntax_mistakes.append(
                    to_logic_mistake(
                        user_id,
                        None,
                        self.process_tip(exception),
                    )
                )

            for syntax_mistake in syntax_mistakes:
                service.repository.create_mistake(syntax_mistake)

            raise e
