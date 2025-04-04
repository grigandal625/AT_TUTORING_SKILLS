import json
from typing import List
from typing import Optional
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
    """Вычисляет расстояние Левенштейна между двумя строками."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


class KBObjectServiceLogicLexic:
    def estimate_object(
        self, user_id: int, task_id: int, obj: KBClass, obj_et: KBClass, context: Context
    ) -> List[CommonMistake]:
        """Оценивает соответствие объекта эталону и возвращает список ошибок."""
        errors_list = []

        # Проверка количества свойств
        if len(obj.properties) < len(obj_et.properties):
            place = json.dumps(context.full_path_list, ensure_ascii=False)
            errors_list.append(
                to_logic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip=f"Введено меньше свойств, чем требуется, в объекте {obj.id}\nрасположение: {place}",
                    coefficients=KNOWLEDGE_COEFFICIENTS,
                    entity_type="object",
                )
            )

        for property_et in obj_et.properties:
            min_distance = 100
            found = False
            closest_property = None

            for prop in obj.properties:
                distance = levenshtein_distance(prop.id, property_et.id)
                if distance < min_distance:
                    min_distance = distance
                    closest_property = prop
                if distance == 0:
                    found = True
                    # Проверка значения свойства
                    if prop.type.id != property_et.type.id:
                        child_context = context.create_child(f"Тип атрибута {property_et.type.id}")
                        place = json.dumps(child_context.full_path_list, ensure_ascii=False)
                        errors_list.append(
                            to_logic_mistake(
                                user_id=user_id,
                                task_id=task_id,
                                tip=f"Неверный тип атрибута '{property_et.id}'. Ожидалось: {property_et.type.id}, получено: {prop.type.id}\nрасположение: {place}",
                                coefficients=KNOWLEDGE_COEFFICIENTS,
                                entity_type="object",
                            )
                        )
                    break

            if not found:
                child_context = context.create_child(f"Атрибут {property_et.id} ")
                place = json.dumps(child_context.full_path_list, ensure_ascii=False)

                if min_distance >= 1:
                    errors_list.append(
                        to_logic_mistake(
                            user_id=user_id,
                            task_id=task_id,
                            tip=f"Отсутствует атрибут '{property_et.id}'\nрасположение: {place}",
                            coefficients=KNOWLEDGE_COEFFICIENTS,
                            entity_type="object",
                        )
                    )

        return errors_list

    async def handle_logic_lexic_mistakes(
        self: "KBObjectService", user: User, task: Task, obj: KBClass, obj_et: KBClass
    ) -> Optional[List[CommonMistake]]:
        """Обрабатывает логические и лексические ошибки в объекте."""
        user_id = user.user_id
        task_id = task.pk
        context = Context(parent=None, name=f"Объект {obj_et.id}")

        errors_list = self.estimate_object(user_id, task_id, obj, obj_et, context)

        if errors_list:
            service = TaskService()
            for mistake in errors_list:
                if isinstance(mistake, CommonMistake):
                    await service.append_mistake(mistake)

            await service.increment_taskuser_attempts(task, user)
            return errors_list

        return None
