from at_tutoring_skills.core.errors.consts import Coefficients
from at_tutoring_skills.core.errors.models import CommonMistake
from at_tutoring_skills.apps.mistakes.models import MISTAKE_TYPE_CHOICES

# class CommonMistake(BaseModel):
# user_id: int
# type: str
# task_id: Optional[int]
# fine: float
# coefficient: float
# tip: str
# is_tip_shown: bool


def to_syntax_mistake(
    user_id: int,
    tip: str,
    coefficients: Coefficients,
    entity_type: str,
) -> CommonMistake:
    return CommonMistake(
        user_id=user_id,
        type="syntax",
        task_id=None,
        fine=coefficients.syntax_fine,
        coefficient=coefficients.entity_fines[entity_type],
        tip=tip,
        is_tip_shown=False,
    )


def to_logic_mistake(
    user_id: int,
    task_id: int,
    tip: str,
    coefficients: Coefficients,
    entity_type: str,
) -> CommonMistake:
    return CommonMistake(
        user_id=user_id,
        type="logic",
        task_id=task_id,
        fine=coefficients.syntax_fine,
        coefficient=coefficients.entity_fines[entity_type],
        tip=tip,
        is_tip_shown=False,
    )


def to_lexic_mistake(
    user_id: int,
    task_id: int,
    tip: str,
    coefficients: Coefficients,
    entity_type: str,
) -> CommonMistake:
    return CommonMistake(
        user_id=user_id,
        type="lexic",
        task_id=task_id,
        fine=coefficients.syntax_fine,
        coefficient=coefficients.entity_fines[entity_type],
        tip=tip,
        is_tip_shown=False,
    )
