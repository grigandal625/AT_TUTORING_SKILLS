from typing import List, Optional

from pydantic import BaseModel


class TemplateUsageArgumentRequest(BaseModel):
    id: Optional[int] = None
    relevant_resource_id: int
    resource_id: int


class TemplateUsageRequest(BaseModel):
    id: Optional[int] = None
    name: str
    template_id: int
    arguments: List[TemplateUsageArgumentRequest]
