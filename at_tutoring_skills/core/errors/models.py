from typing import Literal
from typing import Optional

from pydantic import BaseModel


class CommonMistake(BaseModel):
    user_id: int
    type: Literal["syntax", "logic", "lexic"]
    task_id: Optional[int]
    fine: float
    coefficient: float
    tip: str
    is_tip_shown: bool
