from typing import List, Optional, Union

from pydantic import BaseModel


class ResourceAttributeRequest(BaseModel):
    id: Optional[int] = None
    rta_id: int
    value: Optional[Union[int, float, bool, str]] = None


class ResourceRequest(BaseModel):
    id: Optional[int] = None
    name: str
    to_be_traced: bool
    attributes: List[ResourceAttributeRequest]
    resource_type_id: int