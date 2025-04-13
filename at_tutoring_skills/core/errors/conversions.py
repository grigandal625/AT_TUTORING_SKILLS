from at_tutoring_skills.core.errors.consts import Coefficients
from at_tutoring_skills.core.errors.models import CommonMistake


def to_syntax_mistake(
    user_id: int, tip: str, coefficients: Coefficients, entity_type: str, skills: list[int] = None
) -> CommonMistake:
    skills = skills or []
    return CommonMistake(
        user_id=user_id,
        type="syntax",
        task_id=None,
        fine=coefficients.syntax_fine,
        coefficient=coefficients.entity_fines[entity_type],
        tip=tip,
        is_tip_shown=False,
        skills=skills,
    )


def to_logic_mistake(
    user_id: int, task_id: int, tip: str, coefficients: Coefficients, entity_type: str, skills: list[int] = None
) -> CommonMistake:
    skills = skills or []
    return CommonMistake(
        user_id=user_id,
        type="logic",
        task_id=task_id,
        fine=coefficients.logic_fine,
        coefficient=coefficients.entity_fines[entity_type],
        tip=tip,
        is_tip_shown=False,
        skills=skills,
    )


def to_lexic_mistake(
    user_id: int, task_id: int, tip: str, coefficients: Coefficients, entity_type: str, skills: list[int] = None
) -> CommonMistake:
    skills = skills or []
    return CommonMistake(
        user_id=user_id,
        type="lexic",
        task_id=task_id,
        fine=coefficients.lexic_fine,
        coefficient=coefficients.entity_fines[entity_type],
        tip=tip,
        is_tip_shown=False,
        skills=skills,
    )
