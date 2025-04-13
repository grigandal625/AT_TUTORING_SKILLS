from typing import List
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

from at_krl.core.simple.simple_evaluatable import SimpleEvaluatable
from at_krl.core.simple.simple_operation import SimpleOperation
from at_krl.core.simple.simple_reference import SimpleReference
from at_krl.core.simple.simple_value import SimpleValue
from at_krl.core.temporal.allen_interval import KBInterval  # Изменено с KBEvent на KBInterval
from at_krl.core.temporal.allen_operation import AllenOperation

from at_tutoring_skills.apps.skills.models import Task
from at_tutoring_skills.apps.skills.models import User
from at_tutoring_skills.core.errors.context import Context
from at_tutoring_skills.core.errors.models import CommonMistake
from at_tutoring_skills.core.task.service import TaskService

if TYPE_CHECKING:
    from at_tutoring_skills.core.knowledge_base.interval.service import KBIntervalService


class KBIntervalServiceLogicLexic:  # Изменено с KBEventServiceLogicLexic
    def estimate_condition(self, condition: SimpleEvaluatable, et_condition: SimpleEvaluatable, context: Context):
        errors = []
        return errors

    def estimate_open_condition(
        self,
        user_id: str,
        task_id: int,
        condition: Union[SimpleValue, SimpleReference, SimpleOperation],
        et_condition: Union[SimpleValue, SimpleReference, SimpleOperation],
        context: Context,
    ):
        errors = []
        # errors = self.estimate_condition(self, condition, et_condition)
        return errors

        # value значение

    def get_various_references(
        condition: Union[
            SimpleValue,
            SimpleReference,
            SimpleOperation,
            AllenOperation,
        ],
        iterations: int,
    ):
        variations = []

        if isinstance(condition, SimpleOperation):
            # коммутативность
            if condition.sign in {"eq", "ne", "add", "mul", "and", "or", "xor"}:
                variations.append(SimpleOperation(sign=condition.sign, left=condition.right, right=condition.left))

            # ассоциативность
            if condition.sign in {"add", "mul", "and", "or", "xor"}:
                if isinstance(condition.left, SimpleOperation):
                    if condition.left.sign == condition.sign:
                        op = SimpleOperation(sign=condition.left.sign, left=condition.left.left, right=condition.right)
                        variations.append(SimpleOperation(sign=condition.sign, right=condition.left.right, left=op))

                        op = SimpleOperation(sign=condition.left.sign, left=condition.right, right=condition.left.right)
                        variations.append(SimpleOperation(sign=condition.sign, right=condition.left.right, left=op))

                if isinstance(condition.right, SimpleOperation):
                    if condition.right.sign == condition.sign:
                        op = SimpleOperation(
                            sign=condition.right.sign, left=condition.right.right, right=condition.left
                        )
                        variations.append(SimpleOperation(sign=condition.sign, left=condition.right.right, right=op))

                        op = SimpleOperation(sign=condition.right.sign, left=condition.right.left, right=condition.left)
                        variations.append(SimpleOperation(sign=condition.sign, left=condition.right.left, right=op))
            # дистрибутивность правая
            # if condition.sign in {'mul'}:
            #     if isinstance(condition.right, SimpleOperation):
            #         if condition.right.sign in {'add', 'sub'}:
            #             ...

            # if condition.sign in {'add', 'mul','and', 'or'}:
            #     ...
            # if condition.sign in {}:

        # if isinstance(condition, AllenOperation):
        #     op = get_inversion(condition.sign)

        # "b": {"event_event": True, "event_interval": True, "inversion": "bi"},
        # "bi": {"inversion": "b"},
        # "m": {"inversion": "mi"},
        # "mi": {"inversion": "m"},
        # "s": {"event_interval": True, "inversion": "si"},
        # "si": {"inversion": "s"},
        # "f": {"inversion": "fi"},
        # "fi": {"inversion": "f"},
        # "d": {"event_interval": True, "inversion": "di"},
        # "di": {"inversion": "d"},
        # "o": {"inversion": "oi"},
        # "oi": {"inversion": "o"},
        # "e": {"event_event": True, "inversion": "e"},
        # "a":{"interval_interval": False, "event_interval": True, "inversion": "b"}
        return variations

    def estimate_interval(
        self, user_id: str, task_id: int, etalon_interval: KBInterval, interval: KBInterval, context: Context
    ):  # Изменено estimate_event на estimate_interval
        print("Estimate interval")  # Изменено сообщение
        errors_list = []

        check_open = self.estimate_condition(
            user_id, task_id, etalon_interval.open, interval.open, context=context.create_child("Открытие ")
        )
        check_close = self.estimate_condition(
            user_id, task_id, etalon_interval.close, interval.close, context=context.create_child("Закрытие ")
        )

    async def handle_logic_lexic_mistakes(
        self: "KBIntervalService",
        user: User,
        task: Task,
        interval: KBInterval,
        interval_et: KBInterval,  # Изменено параметры
    ) -> Optional[List[CommonMistake]]:
        """Обрабатывает логические и лексические ошибки в интервале."""  # Изменено описание
        user_id = user.user_id
        task_id = task.pk
        context = Context(parent=None, name=f"Интервал {interval_et.id}")  # Изменено название контекста

        errors_list = self.estimate_interval(user_id, task_id, interval, interval_et, context)  # Изменено вызов метода

        if errors_list:
            service = TaskService()
            for mistake in errors_list:
                if isinstance(mistake, CommonMistake):
                    await service.append_mistake(mistake)

            await service.increment_taskuser_attempts(task, user)
            return errors_list

        return None
