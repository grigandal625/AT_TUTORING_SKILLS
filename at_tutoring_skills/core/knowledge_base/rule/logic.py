import json
from typing import List
from typing import Optional
from typing import TYPE_CHECKING

from at_krl.core.kb_rule import KBRule

from at_tutoring_skills.apps.skills.models import Task
from at_tutoring_skills.apps.skills.models import User
from at_tutoring_skills.core.errors.consts import KNOWLEDGE_COEFFICIENTS
from at_tutoring_skills.core.errors.context import Context
from at_tutoring_skills.core.errors.conversions import to_logic_mistake
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
        context = Context(parent=None, name=f"Объект {rule.id}")
        errors_list = await cond.compare_conditions_deep(user_id, task_id, rule.condition, most_common, 'rule', context, None)
        
        if rule.instructions:
            if rule_et.instructions:
                if len(rule.instructions)< len(rule_et.instructions):
                    place = json.dumps(context.full_path_list, ensure_ascii=False)
                    errors_list.append(
                        to_logic_mistake(
                            user_id=user_id,
                            task_id=task_id,
                            tip=f"Введено меньше условий ТО, чем требуется, в объекте {rule.id}\nрасположение: {place}",
                            coefficients=KNOWLEDGE_COEFFICIENTS,
                            entity_type="rule",
                            skills=[301],
                        )
                    )

                for if_instr_et in rule_et.instructions:
                    found = False

                    for if_instr in rule.instructions:
                        if if_instr.ref.id == if_instr_et.ref.id and if_instr.ref.ref.id == if_instr_et.ref.ref.id:
                            found = True
                            break

                    if not found:
                        place = json.dumps(context.create_child(f"else instruction {if_instr_et.ref.id}").full_path_list, 
                                        ensure_ascii=False)
                        errors_list.append(
                            to_logic_mistake(
                                user_id=user_id,
                                task_id=task_id,
                                tip=f"Не найдено условие ТО {if_instr_et.ref.id}, в правиле {rule.id}\nрасположение: {place}",
                                coefficients=KNOWLEDGE_COEFFICIENTS,
                                entity_type="object",
                                skills=[],
                            )
                        )
                    if found:
                        var = cond.get_various_references(if_instr_et.value, 5)
                        most_common, score = cond.find_most_similar(if_instr.value, var, {'structure': 0.6, 'variables': 0.3, 'constants': 0.1})
                        context = Context(parent=None, name=f"Правило {rule.id}")
                        errors_list = await cond.compare_conditions_deep(user_id, task_id, if_instr.value, most_common, 'rule', context, None)
            else:
                errors_list.append(to_logic_mistake(
                                user_id=user_id,
                                task_id=task_id,
                                tip=f"Созданы лишние условия ТО в правиле {rule.id}\nрасположение: {context.full_path_list}",
                                coefficients=KNOWLEDGE_COEFFICIENTS,
                                entity_type="object",
                                skills=[],
                            ))
            
        if rule.else_instructions:
            if rule_et.else_instructions:
                if len(rule.else_instructions)< len(rule_et.else_instructions):
                    place = json.dumps(context.full_path_list, ensure_ascii=False)
                    errors_list.append(
                        to_logic_mistake(
                            user_id=user_id,
                            task_id=task_id,
                            tip=f"Введено меньше условий ИНАЧЕ, чем требуется, в объекте {rule.id}\nрасположение: {place}",
                            coefficients=KNOWLEDGE_COEFFICIENTS,
                            entity_type="rule",
                            skills=[301],
                        )
                    )

                for else_instr_et in rule.else_instructions:
                    found = False

                    for else_instr in rule.else_instructions:
                        if else_instr.ref.id == else_instr_et.ref.id:
                            found = True
                            break

                    if not found:
                        place = json.dumps(context.create_child(f"else instruction {else_instr.ref.id}").full_path_list, 
                                        ensure_ascii=False)
                        errors_list.append(
                            to_logic_mistake(
                                user_id=user_id,
                                task_id=task_id,
                                tip=f"Не найдено условие ТЕ {else_instr_et.ref.id}, в правиле {rule.id}\nрасположение: {place}",
                                coefficients=KNOWLEDGE_COEFFICIENTS,
                                entity_type="object",
                                skills=[],
                            )
                        )
                    if found:
                        var = cond.get_various_references(else_instr_et.value, 5)
                        most_common, score = cond.find_most_similar(else_instr.value, var, {'structure': 0.6, 'variables': 0.3, 'constants': 0.1})
                        context = Context(parent=None, name=f"Правило {rule.id}")
                        errors_list = await cond.compare_conditions_deep(user_id, task_id, else_instr.value, most_common, 'rule', context, None)
            else:
                errors_list.append(
                    to_logic_mistake(
                                    user_id=user_id,
                                    task_id=task_id,
                                    tip=f"Созданы лишние условия ИНАЧЕ в правиле {rule.id}\nрасположение: {context.full_path_list}",
                                    coefficients=KNOWLEDGE_COEFFICIENTS,
                                    entity_type="object",
                                    skills=[],
                                )
                )
        return errors_list
    
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