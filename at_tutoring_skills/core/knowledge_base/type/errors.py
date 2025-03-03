from at_tutoring_skills.core.models.models import CommonMistake

SYNTAX_FINE = 3
LOGIC_FINE = 2
LEXIC_FINE = 1

COEFFICIENT = 5


def to_syntax_mistake(user_id: int, task_id: int | None, tip: str) -> CommonMistake:
    return CommonMistake(
        user_id=user_id,
        type="KB_TYPE",
        task_id=task_id,
        fine=SYNTAX_FINE,
        coefficient=COEFFICIENT,
        tip=tip,
        is_tip_shown=False,
    )


def to_logic_mistake(user_id: int, task_id: int | None, tip: str) -> CommonMistake:
    return CommonMistake(
        user_id=user_id,
        type="KB_TYPE",
        task_id=task_id,
        fine=LOGIC_FINE,
        coefficient=COEFFICIENT,
        tip=tip,
        is_tip_shown=False,
    )


def to_lexic_mistake(user_id: int, task_id: int | None, tip: str) -> CommonMistake:
    return CommonMistake(
        user_id=user_id,
        type="KB_TYPE",
        task_id=task_id,
        fine=LEXIC_FINE,
        coefficient=COEFFICIENT,
        tip=tip,
        is_tip_shown=False,
    )
