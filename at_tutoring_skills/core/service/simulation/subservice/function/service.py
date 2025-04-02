from typing import List

from at_tutoring_skills.apps.skills.models import Task
from at_tutoring_skills.core.errors.models import CommonMistake

from at_tutoring_skills.apps.skills.models import SUBJECT_CHOICES
from at_tutoring_skills.core.errors.consts import SIMULATION_COEFFICIENTS

from at_tutoring_skills.core.errors.conversions import to_lexic_mistake
from at_tutoring_skills.core.errors.conversions import to_logic_mistake

from at_tutoring_skills.core.service.simulation.subservice.resource_type.dependencies import IMistakeService
from at_tutoring_skills.core.service.simulation.subservice.resource_type.dependencies import ITaskService
from at_tutoring_skills.core.service.simulation.subservice.function.models.models import (
    FunctionParameterRequest,
    FunctionRequest,
)
from at_tutoring_skills.core.service.simulation.subservice.resource_type.models.models import ResourceTypeRequest
from at_tutoring_skills.core.service.simulation.utils.utils import pydantic_mistakes
from at_tutoring_skills.core.task.service import TaskService

class FunctionService:
    mistake_service = None
    main_task_service = None

    def __init__(
        self,
        mistake_service: IMistakeService,
        task_service: ITaskService,
    ):
        self._mistake_service = mistake_service
        self._task_service = task_service
        self.main_task_service = TaskService()

    async def handle_syntax_mistakes(
        self, 
        user_id: int, 
        data: dict
        ) -> FunctionRequest:
        result = pydantic_mistakes(
            user_id=user_id,
            raw_request=data["args"]["func"],
            pydantic_class=FunctionRequest,
            pydantic_class_name="function",
        )

        print("Данные, полученные pydentic моделью: ", result)

        if isinstance(result, FunctionRequest):
            return result
        elif isinstance(result, list) and all(isinstance(err, CommonMistake) for err in result):
            for mistake in result:
                await self.main_task_service.append_mistake(mistake)
                self._mistake_service.create_mistake(mistake, user_id, "syntax")

            raise ValueError("Handle function: syntax mistakes")

        raise TypeError("Handle function: unexpected result")


    async def handle_logic_mistakes(
        self,
        user_id: int,
        function: FunctionRequest,
    ) -> None:
        try:
            task: Task = await self.main_task_service.get_task_by_name(
                function.name, SUBJECT_CHOICES.SIMULATION_FUNCS 
            )
            task_id = task.pk
            object_reference = await self.main_task_service.get_function_reference(task)

            print("Данные object reference, полученные для сравнения: ", object_reference)

        except ValueError:  # NotFoundError
            print("Создан тип ресурса, не касающийся задания")
            return

        mistakes = self._params_logic_mistakes(
            function.params,
            object_reference.params,
            user_id,
            task_id,
        )
        print("Найденные ошибки: ", mistakes)

        if len(mistakes) != 0:
            for mistake in mistakes:
                await self.main_task_service.append_mistake(mistake)

            return mistakes  # raise ValueError("Handle function: logic mistakes")

    async def handle_lexic_mistakes(
        self,
        user_id: int,
        function: FunctionRequest,
    ) -> None:
        try:
            task: Task = await self.main_task_service.get_task_by_name(
                function.name, SUBJECT_CHOICES.SIMULATION_FUNCS 
            )
            task_id = task.pk
            object_reference = await self.main_task_service.get_function_reference(task)

            print("Данные object reference, полученные для сравнения: ", object_reference)


        except ValueError:  # NotFoundError
            return

        mistakes = self._params_lexic_mistakes(
            function.params,
            object_reference.params,
            user_id,
            task_id,
        )

        if len(mistakes) != 0:
            for mistake in mistakes:
                await self.main_task_service.append_mistake(mistake)

            raise ValueError("Handle function: lexic mistakes")

    def _params_logic_mistakes(
        self,
        params: List[FunctionParameterRequest],
        params_reference: List[FunctionParameterRequest],
        user_id: int,
        task_id: int,
    ) -> List[CommonMistake]:
        mistakes = []
        match_params_count = 0

        print(f"Comparing number of parameters: provided={len(params)}, reference={len(params_reference)}")
        if len(params) != len(params_reference):
            mistake = to_logic_mistake(
                user_id=user_id,
                task_id=task_id,
                tip="Указано неправильное количество параметров.",
                coefficients=SIMULATION_COEFFICIENTS,
                entity_type="function",
            )
            mistakes.append(mistake)

        # Создаем словарь для быстрого доступа к эталонным параметрам
        params_reference_dict = {param.name: param for param in params_reference}
        print(f"Reference parameters dictionary: {params_reference_dict}")

        # Обработка предоставленных параметров
        for param in params:
            print(f"\nProcessing parameter: name={param.name}, type={param.type}, default_value={param.default_value}")

            if param.name not in params_reference_dict:
                print(f"Unknown parameter: '{param.name}'")
                mistake = to_logic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip=f"Неизвестный параметр '{param.name}'.",
                    coefficients=SIMULATION_COEFFICIENTS,
                    entity_type="function",
                )
                mistakes.append(mistake)
                continue

            param_reference = params_reference_dict[param.name]
            print(
                f"Found reference parameter: name={param_reference.name}, type={param_reference.type}, default_value={param_reference.default_value}"
            )

            # Проверка типа параметра
            if param.type != param_reference.type:
                print(
                    f"Type mismatch for parameter '{param.name}': provided={param.type}, reference={param_reference.type}"
                )
                mistake = to_logic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip=f"Недопустимый тип параметра '{param.name}'.",
                    coefficients=SIMULATION_COEFFICIENTS,
                    entity_type="function",
                )
                mistakes.append(mistake)
                continue

            # Проверка значения по умолчанию
            if param.default_value != param_reference.default_value:
                print(
                    f"Default value mismatch for parameter '{param.name}': provided={param.default_value}, reference={param_reference.default_value}"
                )
                mistake = to_logic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip=f"Недопустимое значение по умолчанию для параметра '{param.name}'.",
                    coefficients=SIMULATION_COEFFICIENTS,
                    entity_type="function",
                )
                mistakes.append(mistake)
                continue

            # Увеличиваем счетчик совпадений при полном совпадении
            print(f"Parameter '{param.name}' matches the reference.")
            match_params_count += 1

        # Проверка на отсутствующие параметры
        reference_param_names = {param.name for param in params_reference}
        provided_param_names = {param.name for param in params}

        missing_params = reference_param_names - provided_param_names
        print(f"Missing parameters: {missing_params}")
        for param_name in missing_params:
            print(f"Missing required parameter: {param_name}")
            mistake = to_logic_mistake(
                user_id=user_id,
                task_id=task_id,
                tip=f"Отсутствует обязательный параметр '{param_name}'.",
                coefficients=SIMULATION_COEFFICIENTS,
                entity_type="function",
            )
            mistakes.append(mistake)

        return mistakes

    def _params_lexic_mistakes(
        self,
        params: Sequence[FunctionParameterRequest],
        params_reference: Sequence[FunctionParameterRequest],
    ) -> List[CommonMistake]:
        mistakes: List[CommonMistake] = []
        match_attrs_count = 0

        for param in params:
            find_flag = False
            closest_match = None
            for param_reference in params_reference:
                if param.name == param_reference.name:
                    find_flag = True
                    break
                else:
                    distance = self._levenshtein_distance(param.name, param_reference.name)
                    if distance == 1:
                        closest_match = param_reference.name
                        mistake = CommonMistake(
                            message=f"Parameters naming error.",
                        )
                        mistakes.append(mistake)
                        break

        return mistakes

    @staticmethod
    def _levenshtein_distance(s1: str, s2: str) -> int:
        if len(s1) < len(s2):
            return FunctionService._levenshtein_distance(s2, s1)

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
