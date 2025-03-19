from enum import Enum
from typing import List, Optional, Union

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


class ResourceTypeTypesEnum(Enum):
    CONSTANT = "CONSTANT"
    TEMPORAL = "TEMPORAL"


class ResourceTypeRequest(BaseModel):
    id: Optional[int] = None
    name: str
    type: ResourceTypeTypesEnum
    attributes: List[ResourceTypeAttributeRequest]
