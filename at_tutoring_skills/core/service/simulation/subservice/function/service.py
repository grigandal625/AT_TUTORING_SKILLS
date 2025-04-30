from typing import List
from typing import Sequence

from at_tutoring_skills.apps.skills.models import SUBJECT_CHOICES
from at_tutoring_skills.apps.skills.models import Task
from at_tutoring_skills.core.errors.consts import SIMULATION_COEFFICIENTS
from at_tutoring_skills.core.errors.conversions import to_lexic_mistake, to_logic_mistake, to_syntax_mistake
from at_tutoring_skills.core.errors.models import CommonMistake
from at_tutoring_skills.core.service.simulation.subservice.function.models.models import FunctionParameterRequest
from at_tutoring_skills.core.service.simulation.subservice.function.models.models import FunctionRequest
from at_tutoring_skills.core.service.simulation.subservice.resource_type.dependencies import IMistakeService
from at_tutoring_skills.core.service.simulation.subservice.resource_type.dependencies import ITaskService
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

    async def handle_syntax_mistakes(self, user_id: int, data: dict) -> FunctionRequest:
        result = pydantic_mistakes(
            user_id=user_id,
            raw_request=data["args"]["func"],
            pydantic_class=FunctionRequest,
            pydantic_class_name="function",
        )
        errors_list = []

        print("Данные, полученные pydentic моделью: ", result)

        if isinstance(result, FunctionRequest):
            return result
        elif isinstance(result, list) and all(isinstance(err, CommonMistake) for err in result):
            for mistake in result:
                # await self.main_task_service.append_mistake(mistake)
                # self._mistake_service.create_mistake(mistake, user_id, "syntax")

                common_mistake = to_syntax_mistake(
                        user_id=user_id,
                        tip=f"Синтаксическая ошибка при создании функции.\n\n",
                        coefficients=SIMULATION_COEFFICIENTS,
                        entity_type="function",
                        skills=[264],
                )
                errors_list.append(common_mistake)
                await self.main_task_service.append_mistake(common_mistake)

            raise ValueError("Синтаксическая ошибка при создании функции.")


    async def handle_logic_mistakes(
        self,
        user_id: int,
        function: FunctionRequest,
        task: Task
    ) -> None:
    
        task_id = task.pk
        object_reference = await self.main_task_service.get_function_reference(task)

        mistakes = self._params_logic_mistakes(
            function,
            object_reference,
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
        task: Task
    ) -> None:
        try:
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
        function: FunctionRequest,
        function_reference: FunctionRequest,
        params: Sequence[FunctionParameterRequest],
        params_reference: Sequence[FunctionParameterRequest],
        user_id: int,
        task_id: int,
    ) -> List[CommonMistake]:
        mistakes = []
        match_params_count = 0

        print(f"Comparing function: provided={function.ret_type}, reference={function_reference.ret_type}")
        if function.ret_type != function_reference.ret_type:
            mistake = to_logic_mistake(
                user_id=user_id,
                task_id=task_id,
                tip="Указан неправильный тип функции.\n\n",
                coefficients=SIMULATION_COEFFICIENTS,
                entity_type="function",
                skills=[262, 263],
            )
            mistakes.append(mistake)
            return mistakes

        print(f"Comparing function body: provided={function.body}, reference={function_reference.body}")

        # Проверка, является ли body пустой строкой или строкой с пробелами
        if not function.body.strip():
            mistake = to_logic_mistake(
                user_id=user_id,
                task_id=task_id,
                tip="Тело функции не может быть пустым.\n\n",
                coefficients=SIMULATION_COEFFICIENTS,
                entity_type="function",
                skills=[262, 263],
            )
            mistakes.append(mistake)
            return mistakes

        # Проверка на совпадение с эталонным значением
        # if function.body != function_reference.body:
        #     mistake = to_logic_mistake(
        #         user_id=user_id,
        #         task_id=task_id,
        #         tip=f"Указано неверное тело функции. Ожидалось: '{function_reference.body}', получено: '{function.body}'.",
        #         coefficients=SIMULATION_COEFFICIENTS,
        #         entity_type="function",
        #         skills=[262, 263],
        #     )
        #     mistakes.append(mistake)
        #     return mistakes

        print(f"Comparing number of parameters: provided={len(params)}, reference={len(params_reference)}")
        if len(params) != len(params_reference):
            mistake = to_logic_mistake(
                user_id=user_id,
                task_id=task_id,
                tip="Указано неправильное количество параметров.\n\n",
                coefficients=SIMULATION_COEFFICIENTS,
                entity_type="function",
                skills=[261],
            )
            mistakes.append(mistake)

        # Создаем словарь для быстрого доступа к эталонным параметрам
        params_reference_dict = {param.name: param for param in params_reference}
        print(f"Reference parameters dictionary: {params_reference_dict}")

        # Обработка предоставленных параметров
        for param in params:
            print(f"\nProcessing parameter: name={param.name}, type={param.type}")

            if param.name not in params_reference_dict:
                continue

            param_reference = params_reference_dict[param.name]
            print(
                f"Found reference parameter: name={param_reference.name}, type={param_reference.type}"
            )

            # Проверка типа параметра
            if param.type != param_reference.type:
                print(
                    f"Type mismatch for parameter '{param.name}': provided={param.type}, reference={param_reference.type}"
                )
                mistake = to_logic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip=f"Недопустимый тип параметра {param.name}.\n\n",
                    coefficients=SIMULATION_COEFFICIENTS,
                    entity_type="function",
                    skills=[261],
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
                tip=f"Отсутствует обязательный параметр {param_name}.",
                coefficients=SIMULATION_COEFFICIENTS,
                entity_type="function",
            )
            mistakes.append(mistake)

        return mistakes

    def _params_lexic_mistakes(
        self,
        params: Sequence[FunctionParameterRequest],
        params_reference: Sequence[FunctionParameterRequest],
        user_id: int,
        task_id: int,
    ) -> List[CommonMistake]:
        mistakes: List[CommonMistake] = []

        # Создаем словарь для быстрого доступа к эталонным параметрам
        params_reference_dict = {param.name: param for param in params_reference}
        print(f"Reference parameters dictionary: {params_reference_dict}")

        for param in params:
            print(f"\nProcessing parameter: name={param.name}, type={param.type}")

            if param.name in params_reference_dict:
                continue  # Параметр совпадает с эталоном

            closest_match = None
            min_distance = float("inf")

            # Поиск ближайшего совпадения по расстоянию Левенштейна
            for param_reference in params_reference:
                distance = self._levenshtein_distance(param.name, param_reference.name)
                if distance < min_distance:
                    min_distance = distance
                    closest_match = param_reference.name

            if closest_match and min_distance <= 1:
                mistake = to_lexic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip=f"Ошибка в имени параметра: {param.name} не найден, но {closest_match} является ближайшим.",
                    coefficients=SIMULATION_COEFFICIENTS,
                    entity_type="function",
                    skills=[265],
                )
                mistakes.append(mistake)
                print(f"Lexic mistake: Close match found for '{param.name}' -> '{closest_match}'")
            else:
                mistake = to_lexic_mistake(
                    user_id=user_id,
                    task_id=task_id,
                    tip=f"Неизвестный параметр: {param.name} не найден.",
                    coefficients=SIMULATION_COEFFICIENTS,
                    entity_type="function",
                    skills=[265],
                )
                mistakes.append(mistake)
                print(f"Lexic mistake: Unknown parameter '{param.name}'")

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
