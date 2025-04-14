from typing import List, Optional, Union
from dataclasses import dataclass
import json
from at_tutoring_skills.core.errors.context import Context
from at_krl.core.simple.simple_evaluatable import SimpleEvaluatable
from at_krl.core.simple.simple_operation import SimpleOperation
from at_krl.core.simple.simple_reference import SimpleReference
from at_krl.core.simple.simple_value import SimpleValue
from at_krl.core.temporal.allen_operation import AllenOperation
from at_krl.core.temporal.allen_reference import AllenReference

from at_tutoring_skills.apps.skills.models import Task, User
from at_tutoring_skills.core.errors.consts import KNOWLEDGE_COEFFICIENTS
from at_tutoring_skills.core.errors.conversions import to_lexic_mistake, to_logic_mistake
from at_tutoring_skills.core.errors.models import CommonMistake
from at_tutoring_skills.core.knowledge_base.condition.compare_conditions import CompareConditionsService
from at_tutoring_skills.core.task.service import TaskService
from at_krl.core.kb_operation import KBOperation


class ConditionComparisonService(CompareConditionsService):
    async def compare_conditions_deep(
        self,
        user_id: int,
        task_id: int,
        user_condition: Union[SimpleValue, SimpleReference, SimpleOperation, AllenOperation, KBOperation],
        etalon_condition: Union[SimpleValue, SimpleReference, SimpleOperation, AllenOperation, KBOperation],
        entity_type: str,
        context_path: Context = None,
        skills: List[int] = None
    ) -> List[CommonMistake]:
        """
        Рекурсивно сравнивает два условия и возвращает список ошибок CommonMistake
        """
        mistakes = []
        context_path = context_path or Context(name="root")
        skills = skills or [300, 301, 302]
        
        # 1. Проверка типа узла
        if type(user_condition) != type(etalon_condition):
            path = json.dumps(context_path.full_path_list, ensure_ascii=False)
            mistakes.append(to_logic_mistake(
                user_id=user_id,
                task_id=task_id,
                tip=f"Тип узла не совпадает. Ожидалось: {type(etalon_condition).__name__}, "
                    f"получено: {type(user_condition).__name__}\nРасположение: {path}",
                coefficients=KNOWLEDGE_COEFFICIENTS,
                entity_type=entity_type,
                skills=[]
            ))
            return mistakes
        
        # 2. Проверка значений
        if isinstance(etalon_condition, SimpleValue):
            if user_condition.content != etalon_condition.content:
                path = json.dumps(context_path.full_path_list, ensure_ascii=False)
                mistakes.append(to_lexic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip=f"Значение не совпадает. Ожидалось: {etalon_condition.content}, "
                        f"получено: {user_condition.content}\nРасположение: {path}",
                    coefficients=KNOWLEDGE_COEFFICIENTS,
                    entity_type=entity_type,
                    skills=[]
                ))
            return mistakes
        
        # 3. Проверка ссылок
        if isinstance(etalon_condition, SimpleReference):
            if user_condition.id != etalon_condition.id:
                path = json.dumps(context_path.full_path_list, ensure_ascii=False)
                mistakes.append(to_logic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip=f"Ссылка не совпадает. Ожидалось: {etalon_condition.id}, "
                        f"получено: {user_condition.id}\nРасположение: {path}",
                    coefficients=KNOWLEDGE_COEFFICIENTS,
                    entity_type=entity_type,
                    skills=[]
                ))
            
            user_ref = user_condition.ref.id if user_condition.ref else None
            etalon_ref = etalon_condition.ref.id if etalon_condition.ref else None
            
            if user_ref != etalon_ref:
                ref_context = context_path.create_child("ref")
                path = json.dumps(ref_context.full_path_list, ensure_ascii=False)
                mistakes.append(to_logic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip=f"Вложенная ссылка не совпадает. Ожидалось: {etalon_ref}, "
                        f"получено: {user_ref}\nРасположение: {path}",
                    coefficients=KNOWLEDGE_COEFFICIENTS,
                    entity_type=entity_type,
                    skills=[]
                ))
            return mistakes
        
        # 4. Проверка временных операций Аллена
        if isinstance(etalon_condition, AllenOperation):
            # Проверка знака операции
            if user_condition.sign != etalon_condition.sign:
                path = json.dumps(context_path.full_path_list, ensure_ascii=False)
                mistakes.append(to_logic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip=f"Операция Аллена не совпадает. Ожидалось: {etalon_condition.sign}, "
                        f"получено: {user_condition.sign}\nРасположение: {path}",
                    coefficients=KNOWLEDGE_COEFFICIENTS,
                    entity_type=entity_type,
                    skills=[]
                ))
            
            # Проверка левого операнда
            left_mistakes = await self._compare_allen_operands(
                user_id, task_id,
                user_condition.left, etalon_condition.left,
                context_path.create_child("left"),
                entity_type
            )
            mistakes.extend(left_mistakes)
            
            # Проверка правого операнда
            right_mistakes = await self._compare_allen_operands(
                user_id, task_id,
                user_condition.right, etalon_condition.right,
                context_path.create_child("right"),
                entity_type
            )
            mistakes.extend(right_mistakes)
            
            return mistakes
        
        # 5. Проверка простых операций
        if isinstance(etalon_condition, SimpleOperation):
            if user_condition.sign != etalon_condition.sign:
                path = json.dumps(context_path.full_path_list, ensure_ascii=False)
                mistakes.append(to_logic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip=f"Операция не совпадает. Ожидалось: {etalon_condition.sign}, "
                        f"получено: {user_condition.sign}\nРасположение: {path}",
                    coefficients=KNOWLEDGE_COEFFICIENTS,
                    entity_type=entity_type,
                    skills=[]
                ))
            
            left_mistakes = await self.compare_conditions_deep(
                user_id, task_id,
                user_condition.left, etalon_condition.left,
                entity_type, context_path, skills
            )
            mistakes.extend(left_mistakes)
            
            right_mistakes = await self.compare_conditions_deep(
                user_id, task_id,
                user_condition.right, etalon_condition.right,
                entity_type, context_path, skills
            )
            
            mistakes.extend(right_mistakes)
        
        return mistakes

    async def _compare_allen_operands(
        self,
        user_id: int,
        task_id: int,
        user_operand: AllenReference,
        etalon_operand: AllenReference,
        context_path: Context,
        entity_type: str
    ) -> List[CommonMistake]:
        """Сравнивает операнды AllenOperation по заданным правилам"""
        mistakes = []
        
        # 1. Проверка типа target
        if type(user_operand.target) != type(etalon_operand.target):
            path = json.dumps(context_path.full_path_list, ensure_ascii=False)
            mistakes.append(to_logic_mistake(
                user_id=user_id,
                task_id=task_id,
                tip=f"Тип цели операнда Аллена не совпадает. Ожидалось: {type(etalon_operand.target).__name__}, "
                    f"получено: {type(user_operand.target).__name__}\nРасположение: {path}",
                coefficients=KNOWLEDGE_COEFFICIENTS,
                entity_type=entity_type,
                skills=[]
            ))
            return mistakes
        
        # 2. Проверка id target
        if user_operand.id != etalon_operand.id:
            path = json.dumps(context_path.full_path_list, ensure_ascii=False)
            mistakes.append(to_logic_mistake(
                user_id=user_id,
                task_id=task_id,
                tip=f"ID цели операнда Аллена не совпадает. Ожидалось: {etalon_operand.id}, "
                    f"получено: {user_operand.id}\nРасположение: {path}",
                coefficients=KNOWLEDGE_COEFFICIENTS,
                entity_type=entity_type,
                skills=[]
            ))
        
        return mistakes

    async def handle_condition_comparison(
        self,
        user: User,
        task: Task,
        user_condition: Union[SimpleValue, SimpleReference, SimpleOperation, AllenOperation],
        etalon_condition: Union[SimpleValue, SimpleReference, SimpleOperation, AllenOperation],
        entity_type: str,
        skills: List[int] = None
    ) -> Optional[List[CommonMistake]]:
        """Обрабатывает сравнение условий и сохраняет ошибки в системе"""
        mistakes = await self.compare_conditions_deep(
            user_id=user.user_id,
            task_id=task.pk,
            user_condition=user_condition,
            etalon_condition=etalon_condition,
            entity_type=entity_type,
            skills=skills
        )
        
        if not mistakes:
            return None
        
        service = TaskService()
        for mistake in mistakes:
            await service.append_mistake(mistake)
        
        await service.increment_taskuser_attempts(task, user)
        return mistakes