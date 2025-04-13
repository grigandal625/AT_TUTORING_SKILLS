from typing import List, Union, Set
from functools import lru_cache
from at_krl.core.simple.simple_evaluatable import SimpleEvaluatable
from at_krl.core.simple.simple_operation import SimpleOperation
from at_krl.core.simple.simple_reference import SimpleReference
from at_krl.core.simple.simple_value import SimpleValue
from at_krl.core.temporal.allen_operation import AllenOperation


class ReferenceVariationsService:
    def get_various_references(
        self,
        condition: Union[SimpleValue, SimpleReference, SimpleOperation, AllenOperation],
        max_depth: int = 5,
    ) -> List[Union[SimpleOperation, SimpleValue, SimpleReference, AllenOperation]]:
        """Главная функция: возвращает все варианты преобразований выражения"""
        if max_depth <= 0:
            return []
        
        if isinstance(condition, AllenOperation):
            return self._handle_allen_operation(condition, max_depth)
        elif isinstance(condition, SimpleOperation):
            return self._handle_simple_operation(condition, max_depth)
        return []

    def _handle_allen_operation(
        self,
        condition: AllenOperation,
        max_depth: int
    ) -> List[AllenOperation]:
        """Обрабатывает временные операции Аллена"""
        variations = set()
        variations.update(self._generate_allen_variations(condition))
        return self._remove_duplicates(variations)

    def _generate_allen_variations(
        self,
        op: AllenOperation
    ) -> Set[AllenOperation]:
        """Генерирует варианты для операций Аллена"""
        variations = set()
        sign = op.sign
        left = op.left
        right = op.right
        
        # Добавляем исходную операцию
        variations.add(op)
        
        # Маппинг инверсий операций Аллена
        inversion_map = {
            "b": "bi", "bi": "b",
            "m": "mi", "mi": "m",
            "s": "si", "si": "s",
            "f": "fi", "fi": "f",
            "d": "di", "di": "d",
            "o": "oi", "oi": "o",
            "e": "e",
            "a": "b"
        }
        
        # Добавляем инвертированную операцию
        if sign in inversion_map:
            inverted_sign = inversion_map[sign]
            variations.add(AllenOperation(sign=inverted_sign, left=right, right=left))
        
        # Для коммутативных операций добавляем перестановку аргументов
        if sign == "e":  # 'equals' - коммутативна
            variations.add(AllenOperation(sign=sign, left=right, right=left))
        
        return variations

    def _handle_simple_operation(
        self,
        condition: SimpleOperation,
        max_depth: int
    ) -> List[Union[SimpleOperation, SimpleValue, SimpleReference]]:
        """Обрабатывает простые операции"""
        variations = set()
        variations.update(self._generate_basic_variations(condition))
        variations.update(self._apply_algebraic_rules(condition))
        
        for var in list(variations):
            if isinstance(var, SimpleOperation):
                # Рекурсивно обрабатываем подвыражения
                for left_var in self.get_various_references(var.left, max_depth-1):
                    variations.add(SimpleOperation(sign=var.sign, left=left_var, right=var.right))
                
                for right_var in self.get_various_references(var.right, max_depth-1):
                    variations.add(SimpleOperation(sign=var.sign, left=var.left, right=right_var))
        
        return self._remove_duplicates(variations)

    @lru_cache(maxsize=None)
    def _generate_basic_variations(
        self,
        op: SimpleOperation
    ) -> Set[Union[SimpleOperation, SimpleValue, SimpleReference]]:
        """Генерирует базовые варианты на свойствах операций"""
        variations = set()
        sign, left, right = op.sign, op.left, op.right
        
        # Коммутативность
        if sign in {"eq", "ne", "add", "mul", "and", "or", "xor"}:
            variations.add(SimpleOperation(sign=sign, left=right, right=left))
        
        # Ассоциативность
        if sign in {"add", "mul", "and", "or", "xor"}:
            variations.update(self._handle_associativity(op))
        
        return variations

    def _handle_associativity(
        self,
        op: SimpleOperation
    ) -> Set[SimpleOperation]:
        """Обрабатывает ассоциативные преобразования"""
        variations = set()
        sign, left, right = op.sign, op.left, op.right
        
        # Левый операнд - такая же операция
        if isinstance(left, SimpleOperation) and left.sign == sign:
            # (a op b) op c → a op (b op c)
            new_right = SimpleOperation(sign=sign, left=left.right, right=right)
            variations.add(SimpleOperation(sign=sign, left=left.left, right=new_right))
            
            # (a op b) op c → (a op c) op b
            new_left = SimpleOperation(sign=sign, left=left.left, right=right)
            variations.add(SimpleOperation(sign=sign, left=new_left, right=left.right))
        
        # Правый операнд - такая же операция
        if isinstance(right, SimpleOperation) and right.sign == sign:
            # a op (b op c) → (a op b) op c
            new_left = SimpleOperation(sign=sign, left=left, right=right.left)
            variations.add(SimpleOperation(sign=sign, left=new_left, right=right.right))
            
            # a op (b op c) → b op (a op c)
            new_right = SimpleOperation(sign=sign, left=left, right=right.right)
            variations.add(SimpleOperation(sign=sign, left=right.left, right=new_right))
        
        return variations

    def _apply_algebraic_rules(
        self,
        op: SimpleOperation
    ) -> Set[Union[SimpleOperation, SimpleValue, SimpleReference]]:
        """Применяет алгебраические правила преобразований"""
        variations = set()
        sign, left, right = op.sign, op.left, op.right
        
        # Дистрибутивность
        if sign == "mul":
            variations.update(self._handle_distributivity(op))
        
        # Свойства констант
        variations.update(self._handle_constants(op))
        
        # Законы де Моргана
        if sign in {"and", "or"}:
            variations.update(self._apply_de_morgan(op))
        
        # Двойное отрицание
        variations.update(self._handle_double_negation(op))
        
        return variations

    def _handle_distributivity(
        self,
        op: SimpleOperation
    ) -> Set[SimpleOperation]:
        """Обрабатывает дистрибутивность"""
        variations = set()
        sign, left, right = op.sign, op.left, op.right
        
        # Умножение относительно сложения
        if sign == "mul":
            # a*(b+c) → a*b + a*c
            if isinstance(left, SimpleOperation) and left.sign == "add":
                variations.add(SimpleOperation(
                    sign="add",
                    left=SimpleOperation(sign="mul", left=left.left, right=right),
                    right=SimpleOperation(sign="mul", left=left.right, right=right)
                ))
            
            # (a+b)*c → a*c + b*c
            if isinstance(right, SimpleOperation) and right.sign == "add":
                variations.add(SimpleOperation(
                    sign="add",
                    left=SimpleOperation(sign="mul", left=left, right=right.left),
                    right=SimpleOperation(sign="mul", left=left, right=right.right)
                ))
        
        return variations

    def _handle_constants(
        self,
        op: SimpleOperation
    ) -> Set[Union[SimpleOperation, SimpleValue, SimpleReference]]:
        """Упрощает выражения с константами"""
        variations = set()
        sign, left, right = op.sign, op.left, op.right
        
        # Для арифметических операций
        if sign == "add":
            if isinstance(left, SimpleValue) and left.content == 0:
                variations.add(right)
            if isinstance(right, SimpleValue) and right.content == 0:
                variations.add(left)
        
        if sign == "mul":
            if isinstance(left, SimpleValue) and left.content == 1:
                variations.add(right)
            if isinstance(right, SimpleValue) and right.content == 1:
                variations.add(left)
            if isinstance(left, SimpleValue) and left.content == 0:
                variations.add(SimpleValue(0))
            if isinstance(right, SimpleValue) and right.content == 0:
                variations.add(SimpleValue(0))
        
        # Для логических операций
        if sign == "and":
            if isinstance(left, SimpleValue) and left.content == True:
                variations.add(right)
            if isinstance(right, SimpleValue) and right.content == True:
                variations.add(left)
            if isinstance(left, SimpleValue) and left.content == False:
                variations.add(SimpleValue(False))
            if isinstance(right, SimpleValue) and right.content == False:
                variations.add(SimpleValue(False))
        
        if sign == "or":
            if isinstance(left, SimpleValue) and left.content == False:
                variations.add(right)
            if isinstance(right, SimpleValue) and right.content == False:
                variations.add(left)
            if isinstance(left, SimpleValue) and left.content == True:
                variations.add(SimpleValue(True))
            if isinstance(right, SimpleValue) and right.content == True:
                variations.add(SimpleValue(True))
        
        return variations

    def _apply_de_morgan(
        self,
        op: SimpleOperation
    ) -> Set[SimpleOperation]:
        """Применяет законы де Моргана"""
        variations = set()
        sign, left, right = op.sign, op.left, op.right
        
        if sign == "and":
            # ¬(A ∧ B) → ¬A ∨ ¬B
            if isinstance(left, SimpleOperation) and left.sign == "not":
                if isinstance(right, SimpleOperation) and right.sign == "not":
                    variations.add(SimpleOperation(
                        sign="or",
                        left=left.left,
                        right=right.left
                    ))
        
        if sign == "or":
            # ¬(A ∨ B) → ¬A ∧ ¬B
            if isinstance(left, SimpleOperation) and left.sign == "not":
                if isinstance(right, SimpleOperation) and right.sign == "not":
                    variations.add(SimpleOperation(
                        sign="and",
                        left=left.left,
                        right=right.left
                    ))
        
        return variations

    def _handle_double_negation(
        self,
        op: SimpleOperation
    ) -> Set[Union[SimpleOperation, SimpleValue, SimpleReference]]:
        """Упрощает двойное отрицание"""
        variations = set()
        
        if op.sign == "not":
            if isinstance(op.left, SimpleOperation) and op.left.sign == "not":
                variations.add(op.left.left)
        
        return variations

    def _remove_duplicates(
        self,
        variations: Set[Union[SimpleOperation, SimpleValue, SimpleReference, AllenOperation]]
    ) -> List[Union[SimpleOperation, SimpleValue, SimpleReference, AllenOperation]]:
        """Удаляет дубликаты на основе структурного сравнения"""
        unique = []
        seen = set()
        
        for var in variations:
            key = self._expression_fingerprint(var)
            if key not in seen:
                seen.add(key)
                unique.append(var)
        
        return unique

    def _expression_fingerprint(
        self,
        expr: Union[SimpleOperation, SimpleValue, SimpleReference, AllenOperation]
    ) -> str:
        """Создает уникальный ключ для выражения"""
        if isinstance(expr, SimpleValue):
            return f"V:{expr.content}"
        elif isinstance(expr, SimpleReference):
            return f"R:{expr.id}"
        elif isinstance(expr, SimpleOperation):
            left_fp = self._expression_fingerprint(expr.left)
            right_fp = self._expression_fingerprint(expr.right)
            return f"O:{expr.sign}({left_fp},{right_fp})"
        elif isinstance(expr, AllenOperation):
            return f"A:{expr.sign}({expr.left.id},{expr.right.id})"
        return str(expr)