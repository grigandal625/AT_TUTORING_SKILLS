from pydantic import BaseModel, ValidationError
from pydantic_core import ErrorDetails

from at_tutoring_skills.core.errors.consts import SIMULATION_COEFFICIENTS
from at_tutoring_skills.core.errors.conversions import to_syntax_mistake
from at_tutoring_skills.core.errors.models import CommonMistake


def pydantic_mistakes(
    user_id: int,
    raw_request: dict,
    pydantic_class,
    pydantic_class_name: str,
) -> BaseModel | list[CommonMistake]:
    try:
        validated_data = pydantic_class(**raw_request)
        return validated_data

    except ValidationError as e:
        errors: list[CommonMistake] = []
        for error in e.errors():
            error_message = process_tip(error, pydantic_class_name)
            errors.append(
                to_syntax_mistake(
                    user_id,
                    error_message,
                    SIMULATION_COEFFICIENTS,
                    pydantic_class_name,
                )
            )

        return errors


def process_tip(error: ErrorDetails, pydantic_class_name: str) -> str:
    location = " -> ".join(map(str, error.get("loc", ["неизвестное поле"])))
    message = error.get("msg", "отсутствует")
    return f"""
Произошла синтаксическая ошибка при описании "{pydantic_class_name}".
- Ошибка в поле: {location}.
- Описание ошибки: {message}.
"""
