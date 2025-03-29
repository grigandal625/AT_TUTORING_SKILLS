from typing import List
from typing import Optional
from typing import Union

from pydantic import BaseModel


class ResourceAttributeRequest(BaseModel):
    id: Optional[int] = None
    rta_id: int
    value: Optional[Union[int, float, bool, str]] = None


class ResourceAttributeResponse(ResourceAttributeRequest):
    id: int


class ResourceRequest(BaseModel):
    id: Optional[int] = None
    name: str
    to_be_traced: bool
    attributes: List[ResourceAttributeRequest]
    resource_type_id: int


class ResourceResponse(ResourceRequest):
    id: int
    attributes: List[ResourceAttributeResponse]


class ResourcesResponse(BaseModel):
    resources: List[ResourceResponse]
    total: int
