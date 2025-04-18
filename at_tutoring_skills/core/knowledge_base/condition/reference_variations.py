from typing import List
from typing import Union

from at_krl.core.kb_operation import KBOperation
from at_krl.core.simple.simple_operation import SimpleOperation
from at_krl.core.simple.simple_reference import SimpleReference
from at_krl.core.simple.simple_value import SimpleValue
from at_krl.core.temporal.allen_operation import AllenOperation


class ReferenceVariationsService:
    def get_various_references(
        self,
        condition: Union[SimpleValue, SimpleReference, SimpleOperation, KBOperation, AllenOperation],
        max_depth: int = 5,
    ) -> List[Union[SimpleOperation, KBOperation, SimpleValue, SimpleReference, AllenOperation]]:
        """Главная функция: возвращает все варианты преобразований выражения"""
        if max_depth <= 0:
            return []

        if isinstance(condition, AllenOperation):
            array = self._handle_allen_operation(condition, max_depth)
            array.append(condition)
        elif isinstance(condition, (SimpleOperation, KBOperation)):
            array = self._handle_simple_operation(condition, max_depth)
            array.append(condition)
        if isinstance(condition, (SimpleValue, SimpleReference)):
            array = [condition]

        return array

    def _handle_allen_operation(self, condition: AllenOperation, max_depth: int) -> List[AllenOperation]:
        """Обрабатывает временные операции Аллена"""
        variations = []
        variations.extend(self._generate_allen_variations(condition))
        return self._remove_duplicates(variations)

    def _generate_allen_variations(self, op: AllenOperation) -> List[AllenOperation]:
        """Генерирует варианты для операций Аллена"""
        variations = []
        sign = op.sign
        left = op.left
        right = op.right

        # Добавляем исходную операцию
        variations.append(op)

        # Маппинг инверсий операций Аллена
        inversion_map = {
            "b": "bi",
            "bi": "b",
            "m": "mi",
            "mi": "m",
            "s": "si",
            "si": "s",
            "f": "fi",
            "fi": "f",
            "d": "di",
            "di": "d",
            "o": "oi",
            "oi": "o",
            "e": "e",
            "a": "b",
        }

        # Добавляем инвертированную операцию
        if sign in inversion_map:
            inverted_sign = inversion_map[sign]
            inverted_op = AllenOperation(sign=inverted_sign, left=right, right=left)
            if not self._contains_operation(variations, inverted_op):
                variations.append(inverted_op)

        # Для коммутативных операций добавляем перестановку аргументов
        if sign == "e":  # 'equals' - коммутативна
            swapped_op = AllenOperation(sign=sign, left=right, right=left)
            if not self._contains_operation(variations, swapped_op):
                variations.append(swapped_op)

        return variations

    def _handle_simple_operation(
        self, condition: Union[SimpleOperation, KBOperation], max_depth: int
    ) -> List[Union[SimpleOperation, KBOperation, SimpleValue, SimpleReference]]:
        """Обрабатывает простые операции"""
        variations = []
        variations.extend(self._generate_basic_variations(condition))
        variations.extend(self._apply_algebraic_rules(condition))

        for var in variations[:]:
            if isinstance(var, (SimpleOperation, KBOperation)):
                for left_var in self.get_various_references(var.left, max_depth - 1):
                    new_op = type(var)(sign=var.sign, left=left_var, right=var.right)
                    if not self._contains_operation(variations, new_op):
                        variations.append(new_op)

                for right_var in self.get_various_references(var.right, max_depth - 1):
                    new_op = type(var)(sign=var.sign, left=var.left, right=right_var)
                    if not self._contains_operation(variations, new_op):
                        variations.append(new_op)

        return self._remove_duplicates(variations)

    def _generate_basic_variations(
        self, op: Union[SimpleOperation, KBOperation]
    ) -> List[Union[SimpleOperation, KBOperation, SimpleValue, SimpleReference]]:
        variations = []
        sign, left, right = op.sign, op.left, op.right
        # Коммутативность
        if sign in {"eq", "ne", "add", "mul", "and", "or", "xor"}:
            if isinstance(op, (SimpleOperation, KBOperation)):
                new_op = type(op)(sign=sign, left=right, right=left)

            if not self._contains_operation(variations, new_op):
                variations.append(new_op)

        # Ассоциативность
        if sign in {"add", "mul", "and", "or", "xor"}:
            assoc_variations = self._handle_associativity(op)
            for var in assoc_variations:
                if not self._contains_operation(variations, var):
                    variations.append(var)

        return variations

    def _handle_associativity(
        self, op: Union[SimpleOperation, KBOperation]
    ) -> List[Union[SimpleOperation, KBOperation]]:
        """Обрабатывает ассоциативные преобразования"""
        variations = []
        sign, left, right = op.sign, op.left, op.right

        # Левый операнд - такая же операция
        if isinstance(left, (SimpleOperation, KBOperation)) and left.sign == sign:
            # (a op b) op c → a op (b op c)
            new_right = type(op)(sign=sign, left=left.right, right=right)
            new_op = type(op)(sign=sign, left=left.left, right=new_right)
            if not self._contains_operation(variations, new_op):
                variations.append(new_op)

            # (a op b) op c → (a op c) op b
            new_left = type(op)(sign=sign, left=left.left, right=right)
            new_op = type(op)(sign=sign, left=new_left, right=left.right)
            if not self._contains_operation(variations, new_op):
                variations.append(new_op)

        # Правый операнд - такая же операция
        if isinstance(right, (SimpleOperation, KBOperation)) and right.sign == sign:
            # a op (b op c) → (a op b) op c
            new_left = type(op)(sign=sign, left=left, right=right.left)
            new_op = type(op)(sign=sign, left=new_left, right=right.right)
            if not self._contains_operation(variations, new_op):
                variations.append(new_op)

            # a op (b op c) → b op (a op c)
            new_right = type(op)(sign=sign, left=left, right=right.right)
            new_op = type(op)(sign=sign, left=right.left, right=new_right)
            if not self._contains_operation(variations, new_op):
                variations.append(new_op)

        return variations

    def _apply_algebraic_rules(
        self, op: Union[SimpleOperation, KBOperation]
    ) -> List[Union[SimpleOperation, SimpleValue, SimpleReference, KBOperation]]:
        """Применяет алгебраические правила преобразований"""
        variations = []
        sign, left, right = op.sign, op.left, op.right

        # Дистрибутивность
        if sign == "mul":
            variations.extend(self._handle_distributivity(op))

        # Свойства констант
        variations.extend(self._handle_constants(op))

        # Законы де Моргана
        if sign in {"and", "or"}:
            variations.extend(self._apply_de_morgan(op))

        # Двойное отрицание
        variations.extend(self._handle_double_negation(op))

        return variations

    def _handle_distributivity(
        self, op: Union[SimpleOperation, KBOperation]
    ) -> List[Union[SimpleOperation, KBOperation]]:
        """Обрабатывает дистрибутивность"""
        variations = []
        sign, left, right = op.sign, op.left, op.right

        # Умножение относительно сложения
        if sign == "mul":
            # a*(b+c) → a*b + a*c
            if isinstance(left, (SimpleOperation, KBOperation)) and left.sign == "add":
                new_op = type(op)(
                    sign="add",
                    left=type(op.left)(sign="mul", left=left.left, right=right),
                    right=type(op.right)(sign="mul", left=left.right, right=right),
                )
                if not self._contains_operation(variations, new_op):
                    variations.append(new_op)

            # (a+b)*c → a*c + b*c
            if isinstance(right, (SimpleOperation, KBOperation)) and right.sign == "add":
                new_op = type(op)(
                    sign="add",
                    left=type(op.left)(sign="mul", left=left, right=right.left),
                    right=type(op.right)(sign="mul", left=left, right=right.right),
                )
                if not self._contains_operation(variations, new_op):
                    variations.append(new_op)

        return variations

    def _handle_constants(
        self, op: Union[SimpleOperation, KBOperation]
    ) -> List[Union[SimpleOperation, SimpleValue, SimpleReference, KBOperation]]:
        """Упрощает выражения с константами"""
        variations = []
        sign, left, right = op.sign, op.left, op.right

        # Для арифметических операций
        if sign == "add":
            if isinstance(left, SimpleValue) and left.content == 0:
                variations.append(right)
            if isinstance(right, SimpleValue) and right.content == 0:
                variations.append(left)

        if sign == "mul":
            if isinstance(left, SimpleValue) and left.content == 1:
                variations.append(right)
            if isinstance(right, SimpleValue) and right.content == 1:
                variations.append(left)
            if isinstance(left, SimpleValue) and left.content == 0:
                variations.append(SimpleValue(0))
            if isinstance(right, SimpleValue) and right.content == 0:
                variations.append(SimpleValue(0))

        # Для логических операций
        if sign == "and":
            if isinstance(left, SimpleValue) and left.content is True:
                variations.append(right)
            if isinstance(right, SimpleValue) and right.content is True:
                variations.append(left)
            if isinstance(left, SimpleValue) and left.content is False:
                variations.append(SimpleValue(False))
            if isinstance(right, SimpleValue) and right.content is False:
                variations.append(SimpleValue(False))

        if sign == "or":
            if isinstance(left, SimpleValue) and left.content is False:
                variations.append(right)
            if isinstance(right, SimpleValue) and right.content is False:
                variations.append(left)
            if isinstance(left, SimpleValue) and left.content is True:
                variations.append(SimpleValue(True))
            if isinstance(right, SimpleValue) and right.content is True:
                variations.append(SimpleValue(True))

        return variations

    def _apply_de_morgan(self, op: Union[SimpleOperation, KBOperation]) -> List[Union[SimpleOperation, KBOperation]]:
        """Применяет законы де Моргана"""
        variations = []
        sign, left, right = op.sign, op.left, op.right

        if sign == "and":
            # ¬(A ∧ B) → ¬A ∨ ¬B
            if isinstance(left, (SimpleOperation, KBOperation)) and left.sign == "not":
                if isinstance(right, (SimpleOperation, KBOperation)) and right.sign == "not":
                    new_op = type(op)(sign="or", left=left.left, right=right.left)
                    if not self._contains_operation(variations, new_op):
                        variations.append(new_op)

        if sign == "or":
            # ¬(A ∨ B) → ¬A ∧ ¬B
            if isinstance(left, (SimpleOperation, KBOperation)) and left.sign == "not":
                if isinstance(right, (SimpleOperation, KBOperation)) and right.sign == "not":
                    new_op = type(op)(sign="and", left=left.left, right=right.left)
                    if not self._contains_operation(variations, new_op):
                        variations.append(new_op)

        return variations

    def _handle_double_negation(
        self, op: SimpleOperation
    ) -> List[Union[SimpleOperation, SimpleValue, SimpleReference, KBOperation]]:
        """Упрощает двойное отрицание"""
        variations = []

        if op.sign == "not":
            if isinstance(op.left, (SimpleOperation, KBOperation)) and op.left.sign == "not":
                variations.append(op.left.left)

        return variations

    def _is_same_operation_type(
        self,
        op1: Union[SimpleOperation, KBOperation, SimpleValue, SimpleReference, AllenOperation],
        op2: Union[SimpleOperation, KBOperation, SimpleValue, SimpleReference, AllenOperation],
    ) -> bool:
        """Проверяет, являются ли операции одного типа (учитывая SimpleOperation и KBOperation как одинаковые)"""
        if isinstance(op1, (SimpleOperation, KBOperation)) and isinstance(op2, (SimpleOperation, KBOperation)):
            return True
        return type(op1) == type(op2)

    def _contains_operation(
        self,
        variations: List[Union[SimpleOperation, KBOperation, SimpleValue, SimpleReference, AllenOperation]],
        new_op: Union[SimpleOperation, KBOperation, SimpleValue, SimpleReference, AllenOperation],
    ) -> bool:
        """Проверяет, содержит ли список вариаций данную операцию"""
        for var in variations:
            if self._are_operations_equal(var, new_op):
                return True
        return False

    def _are_operations_equal(
        self,
        op1: Union[SimpleOperation, KBOperation, SimpleValue, SimpleReference, AllenOperation],
        op2: Union[SimpleOperation, KBOperation, SimpleValue, SimpleReference, AllenOperation],
    ) -> bool:
        """Сравнивает две операции на структурное равенство"""
        if not self._is_same_operation_type(op1, op2):
            return False

        if isinstance(op1, (SimpleOperation, KBOperation)):
            return (
                op1.sign == op2.sign
                and self._are_operations_equal(op1.left, op2.left)
                and self._are_operations_equal(op1.right, op2.right)
            )
        elif isinstance(op1, AllenOperation):
            return (
                op1.sign == op2.sign
                and self._are_operations_equal(op1.left, op2.left)
                and self._are_operations_equal(op1.right, op2.right)
            )
        elif isinstance(op1, (SimpleValue, SimpleReference)):
            return str(op1) == str(op2)
        return False

    def _remove_duplicates(
        self, variations: List[Union[SimpleOperation, SimpleValue, SimpleReference, AllenOperation, KBOperation]]
    ) -> List[Union[SimpleOperation, SimpleValue, SimpleReference, AllenOperation, KBOperation]]:
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
        self, expr: Union[SimpleOperation, SimpleValue, SimpleReference, AllenOperation, KBOperation]
    ) -> str:
        """Создает уникальный ключ для выражения"""
        if isinstance(expr, SimpleValue):
            return f"V:{expr.content}"
        elif isinstance(expr, SimpleReference):
            return f"R:{expr.id}"
        elif isinstance(expr, (SimpleOperation, KBOperation)):
            left_fp = self._expression_fingerprint(expr.left)
            right_fp = self._expression_fingerprint(expr.right)
            return f"O:{expr.sign}({left_fp},{right_fp})"
        elif isinstance(expr, AllenOperation):
            left_fp = self._expression_fingerprint(expr.left)
            right_fp = self._expression_fingerprint(expr.right)
            return f"A:{expr.sign}({left_fp},{right_fp})"
        return str(expr)
