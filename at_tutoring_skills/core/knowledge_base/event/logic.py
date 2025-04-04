from typing import List, Union
from typing import Optional
from typing import TYPE_CHECKING

from at_krl.core.simple.simple_operation import SimpleOperation
from at_krl.core.temporal.allen_event import KBEvent

from at_tutoring_skills.apps.skills.models import Task
from at_tutoring_skills.apps.skills.models import User
from at_tutoring_skills.core.errors.context import Context
from at_tutoring_skills.core.errors.models import CommonMistake
from at_tutoring_skills.core.task.service import TaskService
from at_krl.core.simple.simple_evaluatable import SimpleEvaluatable
from at_krl.core.simple.simple_reference import SimpleReference
from at_krl.core.simple.simple_operation import SimpleOperation
from at_krl.core.simple.simple_value import SimpleValue

if TYPE_CHECKING:
    from at_tutoring_skills.core.knowledge_base.event.service import KBEventService


class KBEventServiceLogicLexic:
    def estimate_occurance_condition(
        self, user_id: str, task_id: int, 
        condition: Union[SimpleValue, SimpleReference, SimpleOperation], 
        et_condition: Union[SimpleValue, SimpleReference, SimpleOperation], 
        context : Context
    ):
        ...

    def estimate_event(self, user_id: str, task_id: int, etalon_event: KBEvent, event: KBEvent, context: Context):
        print("Estimate event")
        errors_list = []

        check = self.estimate_occurance_condition(
            user_id, task_id, etalon_event.occurance_condition, event.occurance_condition, context
        )

    async def handle_logic_lexic_mistakes(
        self: "KBEventService", user: User, task: Task, event: KBEvent, event_et: KBEvent
    ) -> Optional[List[CommonMistake]]:
        """Обрабатывает логические и лексические ошибки в событии."""
        user_id = user.user_id
        task_id = task.pk
        context = Context(parent=None, name=f"Событие {event_et.id}")

        errors_list = self.estimate_event(user_id, task_id, event, event_et, context)

        if errors_list:
            service = TaskService()
            for mistake in errors_list:
                if isinstance(mistake, CommonMistake):
                    await service.append_mistake(mistake)

            await service.increment_taskuser_attempts(task, user)
            return errors_list

        return None