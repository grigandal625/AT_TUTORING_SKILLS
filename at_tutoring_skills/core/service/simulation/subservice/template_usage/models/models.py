from typing import List
from typing import Optional

from pydantic import BaseModel


class TemplateUsageArgumentRequest(BaseModel):
    id: Optional[int] = None
    relevant_resource_id: Optional[int] = None
    resource_id: Optional[int] = None
    resource_id_str: Optional[str] = None 


class TemplateUsageRequest(BaseModel):
    id: Optional[int] = None
    name: str
    template_id: Optional[int] = None
    template_id_str: Optional[str] = None 
    arguments: List[TemplateUsageArgumentRequest]
