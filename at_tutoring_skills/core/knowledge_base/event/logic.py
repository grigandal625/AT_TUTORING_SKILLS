from typing import TYPE_CHECKING, List

from at_krl.core.temporal.allen_event import KBEvent

from at_tutoring_skills.apps.skills.models import Task, User
from at_tutoring_skills.core.data_serializers import KBEventDataSerializer
from at_tutoring_skills.core.errors.context import Context
from at_tutoring_skills.core.errors.conversions import to_logic_mistake
from at_tutoring_skills.core.errors.models import CommonMistake
from at_tutoring_skills.core.task.service import TaskService

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

    async def handle_logic_lexic_mistakes(self: "KBEventService", user: User, task: Task, event: KBEvent, event_et: KBEvent):
            user_id = user.user_id
            task_id = task.pk

            errors_list = None
            errors_list = self.estimate_event(user_id, task_id, event, event_et)
            if errors_list:
                # mistakes: list[CommonMistake] = []
                service = TaskService()
                for exception in errors_list:
                    if isinstance(exception, CommonMistake):
                        # добавление в бд
                        await service.append_mistake(exception)

                await service.increment_taskuser_attempts(task, user)

                return errors_list
