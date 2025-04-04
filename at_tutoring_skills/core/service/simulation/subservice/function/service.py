from typing import List
from typing import Sequence


from at_tutoring_skills.core.errors.models import CommonMistake
from at_tutoring_skills.core.service.simulation.subservice.function.dependencies import IMistakeService
from at_tutoring_skills.core.service.simulation.subservice.function.dependencies import ITaskService
from at_tutoring_skills.core.service.simulation.subservice.function.models.models import ( 
    FunctionParameterRequest,
    FunctionRequest
)
from at_tutoring_skills.core.service.simulation.utils.utils import pydantic_mistakes


class FunctionService:
    def __init__(
        self,
        mistake_service: IMistakeService,
        task_service: ITaskService,
    ):
        self._mistake_service = mistake_service
        self._task_service = task_service

    def handle_syntax_mistakes(
        self,
        user_id: int,
        raw_request: dict,
    ) -> FunctionRequest:
        result = pydantic_mistakes(
            user_id=123,
            raw_request=raw_request,
            pydantic_class=FunctionRequest,
            pydantic_class_name="function",
        )

        if isinstance(result, FunctionRequest):
            return result

        elif isinstance(result, list) and all(isinstance(err, CommonMistake) for err in result):
            for mistake in result:
                self._mistake_service.create_mistake(mistake, user_id)

            raise ValueError("Handle function: syntax mistakes")

        raise TypeError("Handle function: unexpected result")

    def handle_logic_mistakes(
        self,
        user_id: int,
        function: FunctionRequest,
    ) -> None:
        try:
            object_reference = self._task_service.get_object_reference(
                function.name,
                FunctionRequest,
            )

        except ValueError:  # NotFoundError
            return

        mistakes = self._params_logic_mistakes(
            function.params,
            object_reference.params,
        )

        if len(mistakes) != 0:
            for mistake in mistakes:
                self._mistake_service.create_mistake(mistake, user_id)

            raise ValueError("Handle function: logic mistakes")

    def handle_lexic_mistakes(
        self,
        user_id: int,
        function: FunctionRequest,
    ) -> None:
        try:
            object_reference = self._task_service.get_object_reference(
                function.name,
                FunctionRequest,
            )

        except ValueError:  # NotFoundError
            return

        mistakes = self._params_lexic_mistakes(
            function.params,
            object_reference.params,
        )

        if len(mistakes) != 0:
            for mistake in mistakes:
                self._mistake_service.create_mistake(mistake, user_id)

            raise ValueError("Handle function: lexic mistakes")

    def _params_logic_mistakes(
        self,
        params: List[FunctionParameterRequest],
        params_reference: List[FunctionParameterRequest],
    ) -> List[CommonMistake]:
        mistakes: List[CommonMistake] = []
        match_params_count = 0

        if len(params) != len(params_reference):
            mistake = CommonMistake(
                message=f"Wrong number of parameters provided.",
            )
            mistakes.append(mistake)

        for attr in params:
            find_flag = False
            for attr_reference in params_reference:
                if attr.name == attr_reference.name:
                    find_flag = True
                    match_params_count += 1
                    if attr.type != attr_reference.type:
                        mistake = CommonMistake(
                            message=f"Invalid parameters type'{attr.name}'.",
                        )
                        mistakes.append(mistake)
                        continue

                    if attr.default_value != attr_reference.default_value:
                        mistake = CommonMistake(
                            message=f"Invalid parameters default value'{attr.name}'.",
                        )
                    mistakes.append(mistake)
                    break

            if not find_flag:
                mistake = CommonMistake(
                    message=f"Unknown parameters'{attr.name}'.",
                )
                mistakes.append(mistake)

        if match_params_count < len(params_reference):
            mistake = CommonMistake(
                message=f"Missing required parameters.",
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
