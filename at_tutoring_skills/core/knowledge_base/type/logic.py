from typing import TYPE_CHECKING

from at_krl.core.fuzzy.membership_function import MembershipFunction
from at_krl.core.kb_type import KBFuzzyType
from at_krl.core.kb_type import KBNumericType
from at_krl.core.kb_type import KBSymbolicType
from at_krl.core.kb_type import KBType

from at_tutoring_skills.core.errors.context import Context 
from at_tutoring_skills.core.errors.context import StudentMistakeException
from at_tutoring_skills.core.errors.conversions import to_logic_mistake
from at_tutoring_skills.core.errors.models import CommonMistake

if TYPE_CHECKING:
    from at_tutoring_skills.core.knowledge_base.type.service import KBTypeService


class KBTypeServiceLogicLexic:
    def estimate_string_type(self, type: KBSymbolicType, type_et: KBSymbolicType, context: Context):
        errors_list = []
        check = type.values
        check_et = type_et.values

        if len(check) < len(check_et):
            errors_list.append(
                StudentMistakeException(
                    msg="Введено меньше значений аттрибутов, чем требуется, в типе {type.id}", context=context
                )
            )

        for j in range(len(check_et)):
            for i in range(len(check)):
                if check_et[j] == check[i]:
                    check[j] = None
                    check_et[j] = None
            if check_et[j] is not None:
                context = context.create_child("Атрибут {check_et[j]}")
                errors_list.append(
                    StudentMistakeException(
                        msg="Введено неверное значение в атрибуте типа {type.id}: {check[i]}", context=context
                    )
                )

        return errors_list

    def estimate_number(self, num1, num2, contex: Context):
        print(" ")
        if num1 != num2:
            return False
        else:
            return True

    def estimate_number_type(self, type_et: KBNumericType, type: KBNumericType, context: Context):
        errors_list = []

        # Перевірка _from
        if not self.estimate_number(type.from_, type_et.from_, context=context.create_child("Значение ОТ")):
            errors_list.append(StudentMistakeException(msg="Введено неверное значение ОТ в типе {type.id}", context=context))

        if not self.estimate_number(type.to_, type_et.to_, context=context.create_child("Значение ОТ")):
            errors_list.append(StudentMistakeException(msg="Введено неверное значение ДО в типе {type.id}", context=context))

        return errors_list

    def estimate_fuzzy_type(self, type_et: KBFuzzyType, type: KBFuzzyType, context: Context):
        errors_list = []
        for mf_et in type_et.membership_functions():
            flag = 0
            for mf in type.membership_functions():
                if mf_et.name == mf.name:
                    flag = 1
                    errors_list.extend(
                        self.estimate_membershipfunction(mf_et, mf, context=context.create_child(f"Функция {mf.name}"))
                    )

            if flag == 0:
                # ЗАГЛУШКА
                errors_list.append(ValueError(msg="", context=context.create_child(f"Функция {mf.name}")))

        return errors_list

    def estimate_membershipfunction(self, mf_et: MembershipFunction, mf: MembershipFunction, context: Context):
        errors_list = []
        if mf_et.min != mf.min:
            errors_list.append(
                StudentMistakeException(
                    msg="Несовпадение минимальных значений для функции {mem_func_et.name}: {mem_func_et.min}",
                    context=context.create_child("Значение МИН : {mem_func_et.min}"),
                )
            )
        if mf_et.max != mf.max:
            errors_list.append(
                StudentMistakeException(
                    msg="Несовпадение максимальных значений для функции {mem_func_et.name}: {mem_func_et.max}",
                    context=context.create_child("Значение МАКС : {mem_func_et.min}"),
                )
            )

        # доработать

        mf_et_points_sorted = sorted(mf_et.points, key=lambda x: x[0])
        mf_points_sorted = sorted(mf.points, key=lambda x: x[0])

        for point_et in mf_et_points_sorted:
            for point in mf_points_sorted:
                if point.x == point_et.x and point.y == point_et.y:
                    flag = 1
            if flag == 0:
                # тут лучше поменять местами
                errors_list.append(
                    StudentMistakeException(
                        msg="Отсутствует точка ({point_et.x}, {point_et.y})",
                        context=context.create_child("Точка ({point_et.x}, {point_et.y})"),
                    )
                )
        return errors_list

    def estimate_type(self, etalon_type: KBType, type: KBType):
        context = Context(parent=None, name="Тип {etalon_type.name}")
        errors_list = []

        if type.id == etalon_type.id:
            if type.meta == "string":
                if isinstance(type, KBSymbolicType):
                    errors_list = self.estimate_string_type(
                        type, etalon_type, context=context.create_child("string type attr")
                    )
            if type.meta == "number":
                if isinstance(type, KBNumericType):
                    errors_list = self.estimate_number_type(
                        type, etalon_type, context=context.create_child("number type attr")
                    )
            if type.meta == "fuzzy":
                if isinstance(type, KBFuzzyType):
                    errors_list = self.estimate_fuzzy_type(
                        type, etalon_type, context=context.create_child("fuzzy type attr")
                    )
        if errors_list:
            raise ExceptionGroup("Были выявлены ошибки", errors_list)  # из всех эксепшнов в списке

    def handle_logic_lexic_mistakes(self: "KBTypeService", user_id: int, type: KBType, type_et: KBType):
        try:
            self.estimate_type(type, type_et)
        except ExceptionGroup as eg:
            for exc in eg.exceptions:
                mistakes: list[CommonMistake] = []
            for exception in exc.detail:
                mistakes.append(
                    to_logic_mistake(
                        user_id,
                        None,
                        self.process_tip(exception),
                    )
                )

            for mistake in mistakes:
                self.repository.create_mistake(mistake)
