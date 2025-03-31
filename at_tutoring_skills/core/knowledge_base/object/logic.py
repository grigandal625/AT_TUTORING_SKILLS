from typing import TYPE_CHECKING

from at_krl.core.kb_class import KBClass

from at_tutoring_skills.apps.skills.models import Task
from at_tutoring_skills.apps.skills.models import User
from at_tutoring_skills.core.errors.consts import KNOWLEDGE_COEFFICIENTS
from at_tutoring_skills.core.errors.context import Context
from at_tutoring_skills.core.errors.conversions import to_logic_mistake
from at_tutoring_skills.core.errors.models import CommonMistake
from at_tutoring_skills.core.task.service import TaskService

if TYPE_CHECKING:
    from at_tutoring_skills.core.knowledge_base.object.service import KBObjectService


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Вычисляет расстояние Левенштейна между двумя строками.

    Расстояние Левенштейна - это минимальное количество операций вставки,
    удаления или замены символа, необходимых для преобразования одной строки в другую.

    Args:
        s1: Первая строка
        s2: Вторая строка

    Returns:
        int: Расстояние Левенштейна между строками
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # Стоимость вставки, удаления или замены
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


class KBObjectServiceLogicLexic:
    def estimate_object(
        self, user_id: int, task_id: int, object: KBClass, object_et: KBClass, context: Context
    ) -> list[CommonMistake]:
        errors_list = []

        for property_et in object_et.properties:
            flag = 0
            min_val = 10
            for property in object.properties:
                context.name = property_et.value
                e = levenshtein_distance(property.value, property_et.value)
                min_val = min(e, min_val)
                if e == 0:
                    flag = 1
                    break

            if flag == 0:
                context_child = context.create_child(f"Атрибут {property_et.value}")
                place = context_child.full_path_list()

                if min_val == 1:
                    errors_list.append(
                        to_logic_mistake(
                            user_id=user_id,
                            task_id=task_id,
                            tip=f"Свойство {property_et.source} является лишним\n расположение: {place}",
                            coefficients=KNOWLEDGE_COEFFICIENTS,
                            entity_type="object",
                        )
                    )
                else:
                    errors_list.append(
                        to_logic_mistake(
                            user_id=user_id,
                            task_id=task_id,
                            tip=f"Свойство {property_et.source} является несовпадающим\n расположение: {place}",
                            coefficients=KNOWLEDGE_COEFFICIENTS,
                            entity_type="object",
                        )
                    )
        return errors_list

    def handle_logic_lexic_mistakes(self: "KBObjectService", user: User, task: Task, obj: KBClass, obj_et: KBClass):
        user_id = user.user_id
        task_id = task.pk
        context = Context(parent=None, name="Объект {obj_et.id}")

        try:
            errors_list = self.estimate_object(user_id, task_id, obj, obj_et, context)
            if errors_list:
                raise ExceptionGroup("Были выявлены ошибки", errors_list)
        except ExceptionGroup as eg:
            service = TaskService()
            for exception in eg.exceptions:
                if isinstance(exception, CommonMistake):
                    service.append_mistake(exception)

            service.increment_existing_attempts(task, user)
            return eg.exceptions
