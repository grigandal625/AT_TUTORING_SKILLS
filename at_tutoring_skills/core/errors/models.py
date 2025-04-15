from typing import List, Literal
from typing import Optional

from pydantic import BaseModel


class CommonMistake(BaseModel):
    user_id: str
    type: Literal["syntax", "logic", "lexic"]
    task_id: Optional[int]
    fine: float
    coefficient: float
    tip: str
    is_tip_shown: bool
    skills : List[int]
