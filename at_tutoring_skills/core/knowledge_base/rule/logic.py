from typing import TYPE_CHECKING, List, Optional

from at_krl.core.kb_rule import KBRule

from at_tutoring_skills.apps.skills.models import Task, User
from at_tutoring_skills.core.errors.context import Context
from at_tutoring_skills.core.errors.models import CommonMistake
from at_tutoring_skills.core.task.service import TaskService


if TYPE_CHECKING:
    from at_tutoring_skills.core.knowledge_base.rule.service import KBRuleService


class KBRuleServiceLogicLexic:
    def estimate_rule(self, exception: str) -> str:
        ...


    async def handle_logic_lexic_mistakes(
        self: "KBRuleService", user: User, task: Task, obj: KBRule, obj_et: KBRule
    ) -> Optional[List[CommonMistake]]:
        """Обрабатывает логические и лексические ошибки в объекте."""
        user_id = user.user_id
        task_id = task.pk
        context = Context(parent=None, name=f"Объект {obj_et.id}")

        # errors_list = self.estimate_rule(user_id, task_id, obj, obj_et, context)
        errors_list = []

        if errors_list:
            service = TaskService()
            for mistake in errors_list:
                if isinstance(mistake, CommonMistake):
                    await service.append_mistake(mistake)

            await service.increment_taskuser_attempts(task, user)
            return errors_list

        return None

