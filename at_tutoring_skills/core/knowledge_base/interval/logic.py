from typing import List
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

from at_krl.core.simple.simple_operation import SimpleOperation
from at_krl.core.simple.simple_reference import SimpleReference
from at_krl.core.simple.simple_value import SimpleValue
from at_krl.core.temporal.allen_interval import KBInterval

from at_tutoring_skills.apps.skills.models import Task
from at_tutoring_skills.apps.skills.models import User
from at_tutoring_skills.core.errors.context import Context
from at_tutoring_skills.core.errors.models import CommonMistake
from at_tutoring_skills.core.knowledge_base.condition.lodiclexic_condition import ConditionComparisonService
from at_tutoring_skills.core.task.service import TaskService

if TYPE_CHECKING:
    from at_tutoring_skills.core.knowledge_base.interval.service import KBIntervalService


class KBIntervalServiceLogicLexic:

    async def estimate_interval(self, user_id: str, task_id: int, interval: KBInterval, etalon_interval: KBInterval, context: Context):
        print("Estimate interval")

        cond = ConditionComparisonService()
        var_open = cond.get_various_references(etalon_interval.open, 3)
        var_close = cond.get_various_references(etalon_interval.close, 3)

        most_common_open, score = cond.find_most_similar(interval.open, var_open, {'structure': 0.6, 'variables': 0.3, 'constants': 0.1})
        most_common_close, score = cond.find_most_similar(interval.close, var_close, {'structure': 0.6, 'variables': 0.3, 'constants': 0.1})
        
        context = Context(parent=None, name=f"Объект {interval.id}")
        
        errors_list_open = await cond.compare_conditions_deep(user_id, task_id, interval.open, most_common_open, 'interval', context, None)
        errors_list_close =  await cond.compare_conditions_deep(user_id, task_id, interval.close, most_common_close, 'interval', context, None)

        errors_list_open.extend(errors_list_close)
        return errors_list_open
        

    async def handle_logic_lexic_mistakes(
        self: "KBIntervalService", user: User, task: Task, interval: KBInterval, interval_et: KBInterval
    ) -> Optional[List[CommonMistake]]:
        """Обрабатывает логические и лексические ошибки в интервале."""
        user_id = user.user_id
        task_id = task.pk
        context = Context(parent=None, name=f"Интервал {interval_et.id}")

        errors_list = await self.estimate_interval(user_id, task_id, interval, interval_et, context)

        if errors_list:
            service = TaskService()
            for mistake in errors_list:
                if isinstance(mistake, CommonMistake):
                    await service.append_mistake(mistake)

            await service.increment_taskuser_attempts(task, user)
            return errors_list

        return None
