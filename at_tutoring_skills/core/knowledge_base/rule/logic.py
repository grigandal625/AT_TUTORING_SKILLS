from typing import List
from typing import Optional
from typing import TYPE_CHECKING

from at_krl.core.kb_rule import KBRule

from at_tutoring_skills.apps.skills.models import Task
from at_tutoring_skills.apps.skills.models import User
from at_tutoring_skills.core.errors.context import Context
from at_tutoring_skills.core.errors.models import CommonMistake
from at_tutoring_skills.core.task.service import TaskService
from at_tutoring_skills.core.knowledge_base.condition.lodiclexic_condition import ConditionComparisonService

if TYPE_CHECKING:
    from at_tutoring_skills.core.knowledge_base.rule.service import KBRuleService


class KBRuleServiceLogicLexic:

    async def estimate_rule(self, user_id: int, task_id: int, rule: KBRule, rule_et: KBRule):
        cond = ConditionComparisonService()
        var = cond.get_various_references(rule_et.condition, 5)
        for v in var:
            print("\n", v.krl)
        most_common, score = cond.find_most_similar(rule.condition, var, {'structure': 0.6, 'variables': 0.3, 'constants': 0.1})
        print("\n\n", most_common.krl)
        context = Context(parent=None, name=f"Объект {rule.id}")
        array = await cond.compare_conditions_deep(user_id, task_id, rule.condition, most_common, 'rule', context, None)
        return array
    
    async def handle_logic_lexic_mistakes(
        self: "KBRuleService", user: User, task: Task, rule: KBRule, rule_et: KBRule
    ) -> Optional[List[CommonMistake]]:
        """Обрабатывает логические и лексические ошибки в объекте."""
        user_id = user.user_id
        task_id = task.pk
        context = Context(parent=None, name=f"Объект {rule.id}")

        # errors_list = self.estimate_rule(user_id, task_id, obj, obj_et, context)
        errors_list = []
        errors_list = await self.estimate_rule(user.pk, task.pk, rule, rule_et)
        return errors_list
        

    


        
