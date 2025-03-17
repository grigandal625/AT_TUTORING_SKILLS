from at_tutoring_skills.core.errors.consts import Coefficients
from at_tutoring_skills.core.errors.models import CommonMistake


def to_syntax_mistake(
    user_id: int,
    task_id: int,
    type: str | None,
    tip: str,
    coefficients: Coefficients,
    entity_type: str,
) -> CommonMistake:
    return CommonMistake(
        user_id=user_id,
        type=type,
        task_id=task_id,
        fine=coefficients.syntax_fine,
        coefficient=coefficients.entity_fines[entity_type],
        tip=tip,
        is_tip_shown=False,
    )


def to_logic_mistake(
    user_id: int,
    task_id: int,
    type: str | None,
    tip: str,
    coefficients: Coefficients,
    entity_type: str,
) -> CommonMistake:
    return CommonMistake(
        user_id=user_id,
        type=type,
        task_id=task_id,
        fine=coefficients.syntax_fine,
        coefficient=coefficients.entity_fines[entity_type],
        tip=tip,
        is_tip_shown=False,
    )


def to_lexic_mistake(
    user_id: int,
    task_id: int,
    type: str | None,
    tip: str,
    coefficients: Coefficients,
    entity_type: str,
) -> CommonMistake:
    return CommonMistake(
        user_id=user_id,
        type=type,
        task_id=task_id,
        fine=coefficients.syntax_fine,
        coefficient=coefficients.entity_fines[entity_type],
        tip=tip,
        is_tip_shown=False,
    )
