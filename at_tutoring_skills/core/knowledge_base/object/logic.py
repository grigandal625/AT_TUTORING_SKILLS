from typing import TYPE_CHECKING

from at_krl.core.kb_class import KBClass

from at_tutoring_skills.core.errors import Context
from at_tutoring_skills.core.errors import InvalidCharacter
from at_tutoring_skills.core.errors import Typo
from at_tutoring_skills.core.knowledge_base.errors import to_logic_mistake
from at_tutoring_skills.core.models.models import CommonMistake

if TYPE_CHECKING:
    from at_tutoring_skills.core.knowledge_base.object.service import KBObjectService


class KBObjectServiceLogicLexic:
    def estimate_object(self, object_et: KBClass, object: KBClass, context: Context):
        errors_list = []

        for property_et in object_et.properties:
            flag = 0
            min_val = 10
            for property in object.properties:
                e = 0
                # Comparison.levenshtein_distance(property.value, property_et.value)
                min_val = min(e, min_val)
                if e == 0:
                    flag = 1
                    break

            if flag == 0:
                if min_val == 1:
                    errors_list.append(
                        Typo(
                            msg="Свойство {property_et.source} является лишним",
                            context=context.create_child("атрибут {property_et}"),
                        )
                    )
                else:
                    errors_list.append(
                        InvalidCharacter(
                            msg="Свойство {property_et.source} является несовпадающим",
                            context=context.create_child("Атрибут {property_et.value}"),
                        )
                    )
        if errors_list:
            raise ExceptionGroup("Ошибки при оценке объекта", errors_list)

    def process_tip(self, exception: str) -> str:
        ...

    def handle_logic_lexic_mistakes(self: "KBObjectService", user_id: int, obj: KBClass, obj_et: KBClass) -> KBClass:
        try:
            self.estimate_object(obj, obj_et)
        except ExceptionGroup as eg:
            for exc in eg.exceptions:
                logic_mistakes: list[CommonMistake] = []
                for exception in eg.detail:
                    logic_mistakes.append(
                        to_logic_mistake(
                            user_id,
                            None,
                            self.process_tip(exception),
                        )
                    )

                for syntax_mistake in logic_mistakes:
                    self.repository.create_mistake(syntax_mistake)
