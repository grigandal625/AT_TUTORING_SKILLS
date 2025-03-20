from typing import TYPE_CHECKING

from at_krl.core.temporal.allen_interval import KBInterval

from at_tutoring_skills.core.errors import Context
from at_tutoring_skills.core.errors.models import CommonMistake

if TYPE_CHECKING:
    from at_tutoring_skills.core.knowledge_base.interval.service import KBIntervalService


class KBIntervalServiceLogixLexic:
    def process_tip(self, exception: str) -> str:
        ...

    def estimate_interval(self, etalon_event: dict, event: KBInterval, context: Context):
        print("Estimate event")

        # event_et = KBInterval.from_dict(etalon_event)
        # if event_et.id== event.id:
        #     self.estimate_condition(event_et.occurance_condition,
        #                               event.occurance_condition,
        #                               context=context.create_child('open condition'))

    def handle_logic_lexic_mistakes(
        self: "KBIntervalService", user_id: int, event: KBInterval, event_et: KBInterval
    ) -> KBInterval:
        try:
            self.estimate_interval(event, event_et)
        except ExceptionGroup as eg:
            for exc in eg.exceptions:
                logic_mistakes: list[CommonMistake] = []
                for exception in eg.detail:
                    logic_mistakes.append(
                        self.to_syntax_mistake(
                            user_id,
                            None,
                            self.process_tip(exception),
                        )
                    )

                for syntax_mistake in logic_mistakes:
                    self.repository.create_mistake(syntax_mistake)

                raise exc
