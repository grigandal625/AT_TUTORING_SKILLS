from typing import List
from typing import Optional
from typing import Union

from pydantic import BaseModel


class ResourceAttributeRequest(BaseModel):
    id: Optional[int] = None
    rta_id: Optional[int] = None
    value: Optional[Union[int, float, bool, str]] = None
    name: str


class ResourceAttributeResponse(ResourceAttributeRequest):
    id: int


class ResourceRequest(BaseModel):
    id: Optional[int] = None
    name: str
    to_be_traced: bool = False
    attributes: List[ResourceAttributeRequest]
    resource_type_id: Optional[int] = None
    resource_type_id_str: Optional[str] = None


class ResourceResponse(ResourceRequest):
    id: int
    attributes: List[ResourceAttributeResponse]


class ResourcesResponse(BaseModel):
    resources: List[ResourceResponse]
    total: int
