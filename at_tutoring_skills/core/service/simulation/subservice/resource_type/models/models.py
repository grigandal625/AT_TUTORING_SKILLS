from enum import Enum
from typing import List
from typing import Optional
from typing import Union

from pydantic import BaseModel


class BaseTypesEnum(Enum):
    INT = "INT"
    FLOAT = "FLOAT"
    BOOL = "BOOL"
    ENUM = "ENUM"


class ResourceTypeAttributeRequest(BaseModel):
    id: Optional[int] = None
    name: str
    type: BaseTypesEnum
    enum_values_set: Optional[List[str]] = None
    default_value: Optional[Union[int, float, bool, str]] = None


class ResourceTypeAttributeResponse(ResourceTypeAttributeRequest):
    id: int


class ResourceTypeTypesEnum(Enum):
    CONSTANT = "constant"
    TEMPORAL = "temporal"


class ResourceTypeRequest(BaseModel):
    id: Optional[int] = None
    name: str
    type: ResourceTypeTypesEnum
    attributes: List[ResourceTypeAttributeRequest]


class ResourceTypeResponse(ResourceTypeRequest):
    id: int
    attributes: List[ResourceTypeAttributeResponse]


class ResourceTypesResponse(BaseModel):
    resource_types: List[ResourceTypeResponse]
    total: int
