from typing import List, Union, Tuple, Dict, Set
from math import inf
from at_krl.core.simple.simple_operation import SimpleOperation
from at_krl.core.simple.simple_reference import SimpleReference
from at_krl.core.simple.simple_value import SimpleValue
from at_krl.core.temporal.allen_operation import AllenOperation
from at_krl.core.temporal.allen_reference import AllenReference
from at_krl.core.kb_operation import KBOperation
from at_tutoring_skills.core.knowledge_base.condition.reference_variations import ReferenceVariationsService


class CompareConditionsService(ReferenceVariationsService):
    def find_most_similar(
        self,
        condition: Union[SimpleValue, SimpleReference, SimpleOperation, AllenOperation, KBOperation],
        variations: List[Union[SimpleValue, SimpleReference, SimpleOperation, AllenOperation, KBOperation]],
        weights: Dict[str, float] = {'structure': 0.6, 'variables': 0.3, 'constants': 0.1}
    ) -> Tuple[Union[SimpleValue, SimpleReference, SimpleOperation, AllenOperation, KBOperation], float]:
        """
        Находит наиболее похожее выражение из variations на condition
        
        Параметры:
            condition: исходное выражение для сравнения
            variations: список вариантов для поиска
            weights: веса для компонентов схожести:
                - structure: схожесть структуры выражения
                - variables: схожесть переменных
                - constants: схожесть констант
        
        Возвращает:
            Кортеж из (наиболее похожее выражение, оценка схожести 0-1)
        """
        if not variations:
            return None, 0.0
        
        best_match = None
        best_score = -1
        
        # Предварительно вычисляем характеристики исходного выражения
        cond_fingerprint = self._get_expression_fingerprint(condition)
        
        for variant in variations:
            # Быстрая проверка по fingerprint для полного совпадения
            var_fingerprint = self._get_expression_fingerprint(variant)
            if var_fingerprint == cond_fingerprint:
                return variant, 1.0
            
            # Вычисляем комплексную меру схожести
            similarity = self._calculate_similarity(condition, variant, weights)
            
            if similarity > best_score:
                best_score = similarity
                best_match = variant
        
        return best_match, best_score

    def _calculate_similarity(
        self,
        expr1: Union[SimpleValue, SimpleReference, SimpleOperation, AllenOperation, KBOperation],
        expr2: Union[SimpleValue, SimpleReference, SimpleOperation, AllenOperation, KBOperation],
        weights: Dict[str, float]
    ) -> float:
        """
        Вычисляет меру схожести между двумя выражениями (0-1)
        """
        # 1. Схожесть структуры
        struct_sim = self._structural_similarity(expr1, expr2)
        
        # 2. Схожесть переменных
        vars_sim = self._variables_similarity(expr1, expr2)
        
        # 3. Схожесть констант
        const_sim = self._constants_similarity(expr1, expr2)
        
        # Взвешенная сумма
        total_sim = (
            weights['structure'] * struct_sim +
            weights['variables'] * vars_sim +
            weights['constants'] * const_sim
        )
        
        return total_sim

    def _structural_similarity(
        self,
        expr1: Union[SimpleValue, SimpleReference, SimpleOperation, AllenOperation, KBOperation],
        expr2: Union[SimpleValue, SimpleReference, SimpleOperation, AllenOperation, KBOperation]
    ) -> float:
        """
        Вычисляет схожесть структуры выражений (0-1)
        """
        if type(expr1) != type(expr2):
            return 0.0
        
        if isinstance(expr1, SimpleValue):
            return 1.0 if expr1.content == expr2.content else 0.0
        
        if isinstance(expr1, SimpleReference):
            if expr1.id == expr2.id:
                if expr1.ref is None and expr2.ref is None:
                    return 1.0
                if expr1.ref is not None and expr2.ref is not None and expr1.ref.id == expr2.ref.id:
                    return 1.0
            return 0.0
        
        if isinstance(expr1, AllenOperation):
            if expr1.sign != expr2.sign:
                return 0.0
            return 1.0 if expr1.left.id == expr2.left.id and expr1.right.id == expr2.right.id else 0.0
        
        if isinstance(expr1, (SimpleOperation, KBOperation)):
            if expr1.sign != expr2.sign:
                return 0.0
            
            left_sim = self._structural_similarity(expr1.left, expr2.left)
            right_sim = self._structural_similarity(expr1.right, expr2.right)
            
            return 0.5 * left_sim + 0.5 * right_sim
        
        return 0.0

    def _variables_similarity(
        self,
        expr1: Union[SimpleValue, SimpleReference, SimpleOperation, AllenOperation, KBOperation],
        expr2: Union[SimpleValue, SimpleReference, SimpleOperation, AllenOperation, KBOperation]
    ) -> float:
        """
        Вычисляет схожесть переменных в выражениях (0-1)
        """
        vars1 = self._extract_variables(expr1)
        vars2 = self._extract_variables(expr2)
        
        if not vars1 and not vars2:
            return 1.0
        
        common = vars1 & vars2
        total = vars1 | vars2
        
        return len(common) / len(total) if total else 1.0

    def _constants_similarity(
        self,
        expr1: Union[SimpleValue, SimpleReference, SimpleOperation, AllenOperation, KBOperation],
        expr2: Union[SimpleValue, SimpleReference, SimpleOperation, AllenOperation, KBOperation]
    ) -> float:
        """
        Вычисляет схожесть констант в выражениях (0-1)
        """
        consts1 = self._extract_constants(expr1)
        consts2 = self._extract_constants(expr2)
        
        if not consts1 and not consts2:
            return 1.0
        
        common = 0
        for c1 in consts1:
            for c2 in consts2:
                if c1 == c2:
                    common += 1
                    break
        
        total = len(consts1) + len(consts2)
        
        return (2 * common) / total if total else 1.0

    def _extract_variables(
        self,
        expr: Union[SimpleValue, SimpleReference, SimpleOperation, AllenOperation, KBOperation]
    ) -> Set[str]:
        """Извлекает все переменные из выражения"""
        variables = set()
        
        if isinstance(expr, (SimpleReference, AllenReference)):
            variables.add(expr.id)
        elif isinstance(expr, (SimpleOperation, AllenOperation, KBOperation)):
            variables.update(self._extract_variables(expr.left))
            variables.update(self._extract_variables(expr.right))
        
        return variables

    def _extract_constants(
        self,
        expr: Union[SimpleValue, SimpleReference, SimpleOperation, AllenOperation, KBOperation]
    ) -> List[Union[int, float, str, bool]]:
        """Извлекает все константы из выражения"""
        constants = []
        
        if isinstance(expr, SimpleValue):
            constants.append(expr.content)
        elif isinstance(expr, (SimpleOperation, AllenOperation, KBOperation)):
            constants.extend(self._extract_constants(expr.left))
            constants.extend(self._extract_constants(expr.right))
        
        return constants

    def _get_expression_fingerprint(
        self,
        expr: Union[SimpleValue, SimpleReference, SimpleOperation, AllenOperation, KBOperation]
    ) -> str:
        """
        Создает уникальный отпечаток выражения для быстрого сравнения
        """
        if isinstance(expr, SimpleValue):
            return f"VAL:{expr.content}"
        elif isinstance(expr, SimpleReference):
            ref_part = f".{expr.ref.id}" if expr.ref else ""
            return f"REF:{expr.id}{ref_part}"
        elif isinstance(expr, AllenOperation):
            return f"ALLEN:{expr.sign}({expr.left.id},{expr.right.id})"
        elif isinstance(expr, (SimpleOperation, KBOperation)):
            left = self._get_expression_fingerprint(expr.left)
            right = self._get_expression_fingerprint(expr.right)
            return f"OP:{expr.sign}({left},{right})"
        return ""