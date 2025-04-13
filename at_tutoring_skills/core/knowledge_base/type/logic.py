import json
from typing import TYPE_CHECKING

from at_krl.core.fuzzy.membership_function import MembershipFunction
from at_krl.core.kb_type import KBFuzzyType
from at_krl.core.kb_type import KBNumericType
from at_krl.core.kb_type import KBSymbolicType
from at_krl.core.kb_type import KBType

from at_tutoring_skills.apps.skills.models import Task
from at_tutoring_skills.apps.skills.models import User
from at_tutoring_skills.core.errors.consts import KNOWLEDGE_COEFFICIENTS
from at_tutoring_skills.core.errors.context import Context
from at_tutoring_skills.core.errors.conversions import to_lexic_mistake
from at_tutoring_skills.core.errors.conversions import to_logic_mistake
from at_tutoring_skills.core.errors.models import CommonMistake
from at_tutoring_skills.core.task.service import TaskService

if TYPE_CHECKING:
    from at_tutoring_skills.core.knowledge_base.type.service import KBTypeService


class KBTypeServiceLogicLexic:
    def estimate_string_type(
        self, user_id: int, task_id: int, type: KBSymbolicType, type_et: KBSymbolicType, context: Context
    ):
        errors_list = []
        check = type.values
        check_et = type_et.values

        if len(check) < len(check_et):
            place = json.dumps(context.full_path_list, ensure_ascii=False)
            errors_list.append(
                to_logic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip=f"Введено меньше значений аттрибутов, чем требуется, в типе {type.id} \n расположение: {place}",
                    coefficients=KNOWLEDGE_COEFFICIENTS,
                    entity_type="type",
                    skills=[221],
                )
            )

        for j in range(len(check_et)):
            for i in range(len(check)):
                if check_et[j] == check[i]:
                    check[j] = None
                    check_et[j] = None
            if check_et[j] is not None:
                context = context.create_child(f"Атрибут {check_et[j]}")
                place = json.dumps(context.full_path_list, ensure_ascii=False)
                errors_list.append(
                    to_lexic_mistake(
                        user_id=user_id,
                        task_id=task_id,
                        tip=f"Введено неверное значение в атрибуте типа {type.id}: {check[i]}\n расположение: {place}",
                        coefficients=KNOWLEDGE_COEFFICIENTS,
                        entity_type="type",
                        skills=[220],
                    )
                )

        return errors_list

    def estimate_number(self, num1, num2, contex: Context):
        print(" ")
        if num1 != num2:
            return False
        else:
            return True

    def estimate_number_type(
        self, user_id: int, task_id: int, type: KBNumericType, type_et: KBNumericType, context: Context
    ):
        errors_list = []

        # Перевірка _from
        if type.from_ != type_et.from_:
            context = context.create_child("Значение ОТ")
            place = json.dumps(context.full_path_list, ensure_ascii=False)
            errors_list.append(
                to_lexic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip=f"Введено неверное значение ОТ в типе {type.id}\n расположение: {place}",
                    coefficients=KNOWLEDGE_COEFFICIENTS,
                    entity_type="type",
                    skills=[210],
                )
            )

        if type.to_ != type_et.to_:
            context = context.create_child("Значение ДО")
            place = json.dumps(context.full_path_list, ensure_ascii=False)
            errors_list.append(
                to_lexic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip=f"Введено неверное значение ДО в типе {type.id}\n расположение: {place}",
                    coefficients=KNOWLEDGE_COEFFICIENTS,
                    entity_type="type",
                    skills=[210],
                )
            )

        return errors_list

    def estimate_fuzzy_type(
        self, user_id: int, task_id: int, type: KBFuzzyType, type_et: KBFuzzyType, context: Context
    ):
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
                place = json.dumps(context.full_path_list, ensure_ascii=False)
                errors_list.append(
                    to_logic_mistake(
                        user_id=user_id,
                        task_id=task_id,
                        tip=f"Отсутствует функция {mf.name}\n расположение: {place}",
                        coefficients=KNOWLEDGE_COEFFICIENTS,
                        entity_type="type",
                    )
                )

        return errors_list

    def estimate_membershipfunction(
        self, user_id: int, task_id: int, mf_et: MembershipFunction, mf: MembershipFunction, context: Context
    ):
        errors_list = []
        if mf_et.min != mf.min:
            context = context.create_child("Значение ОТ")
            place = json.dumps(context.full_path_list, ensure_ascii=False)
            errors_list.append(
                to_logic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip=f"Несовпадение минимальных значений для функции {mf_et.name}: {mf_et.min}\n расположение: {place}",
                    coefficients=KNOWLEDGE_COEFFICIENTS,
                    entity_type="type",
                )
            )
        if mf_et.max != mf.max:
            context = context.create_child("Значение ДО")
            place = json.dumps(context.full_path_list, ensure_ascii=False)
            errors_list.append(
                to_logic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip=f"Несовпадение максимальных значений для функции {mf_et.name}: {mf_et.max}\n расположение: {place}",
                    coefficients=KNOWLEDGE_COEFFICIENTS,
                    entity_type="type",
                )
            )

        mf_et_points_sorted = sorted(mf_et.points, key=lambda x: x[0])
        mf_points_sorted = sorted(mf.points, key=lambda x: x[0])

        for point_et in mf_et_points_sorted:
            flag = 0
            for point in mf_points_sorted:
                if point.x == point_et.x and point.y == point_et.y:
                    flag = 1
            if flag == 0:
                place = json.dumps(context.full_path_list, ensure_ascii=False)
                errors_list.append(
                    to_logic_mistake(
                        user_id=user_id,
                        task_id=task_id,
                        tip=f"Отсутствует точка ({point_et.x}, {point_et.y})",
                        coefficients=KNOWLEDGE_COEFFICIENTS,
                        entity_type="type",
                    )
                )
        return errors_list

    def estimate_type(self, user_id: int, task_id: int, type: KBType, etalon_type: KBType):
        context = Context(parent=None, name=f"Тип {etalon_type.id}\n")
        errors_list = []

        if type.id == etalon_type.id:
            if type.meta == "string":
                if isinstance(type, KBSymbolicType):
                    errors_list = self.estimate_string_type(
                        user_id, task_id, type, etalon_type, context=context.create_child("Атрибут ")
                    )
            if type.meta == "number":
                if isinstance(type, KBNumericType):
                    errors_list = self.estimate_number_type(
                        user_id, task_id, type, etalon_type, context=context.create_child("Атрибут ")
                    )
            if type.meta == "fuzzy":
                if isinstance(type, KBFuzzyType):
                    errors_list = self.estimate_fuzzy_type(
                        user_id, task_id, type, etalon_type, context=context.create_child("Атрибут ")
                    )
        if errors_list:
            return errors_list

    async def handle_logic_lexic_mistakes(self: "KBTypeService", user: User, task: Task, type: KBType, type_et: KBType):
        user_id = user.user_id
        task_id = task.pk

        errors_list = None
        errors_list = self.estimate_type(user_id, task_id, type, type_et)
        if errors_list:
            # mistakes: list[CommonMistake] = []
            service = TaskService()
            for exception in errors_list:
                if isinstance(exception, CommonMistake):
                    # добавление в бд
                    await service.append_mistake(exception)

            await service.increment_taskuser_attempts(task, user)

            return errors_list
