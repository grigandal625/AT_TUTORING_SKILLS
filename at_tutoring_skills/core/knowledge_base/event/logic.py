from typing import List
from typing import Optional
from typing import TYPE_CHECKING

from at_krl.core.temporal.allen_event import KBEvent

from at_tutoring_skills.apps.skills.models import Task
from at_tutoring_skills.apps.skills.models import User
from at_tutoring_skills.core.errors.context import Context
from at_tutoring_skills.core.errors.models import CommonMistake
from at_tutoring_skills.core.knowledge_base.condition.lodiclexic_condition import ConditionComparisonService
from at_tutoring_skills.core.task.service import TaskService

if TYPE_CHECKING:
    from at_tutoring_skills.core.knowledge_base.event.service import KBEventService


class KBEventServiceLogicLexic:
    async def estimate_event(self, user_id: str, task_id: int, event: KBEvent, etalon_event: KBEvent, context: Context):
        print("Estimate event")

        cond = ConditionComparisonService()
        var = cond.get_various_references(etalon_event.occurance_condition, 3)
        most_common, score = cond.find_most_similar(
            event.occurance_condition, var, {"structure": 0.6, "variables": 0.3, "constants": 0.1}
        )
        context = Context(parent=None, name=f"Объект {event.id}")
        errors_list = await cond.compare_conditions_deep(
            user_id, task_id, event.occurance_condition, most_common, "event", context, None
        )
        if errors_list:
            for e in errors_list:
                e.skills.append(1401)

        return errors_list

    async def handle_logic_lexic_mistakes(
        self: "KBEventService", user: User, task: Task, event: KBEvent, event_et: KBEvent
    ) -> Optional[List[CommonMistake]]:
        """Обрабатывает логические и лексические ошибки в событии."""
        user_id = user.user_id
        task_id = task.pk
        context = Context(parent=None, name=f"Событие {event_et.id}")

        errors_list = await self.estimate_event(user_id, task_id, event, event_et, context)

        if errors_list:
            service = TaskService()
            for mistake in errors_list:
                if isinstance(mistake, CommonMistake):
                    await service.append_mistake(mistake)

            await service.increment_taskuser_attempts(task, user)
            return errors_list

        return None
