from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ValidationError


class BaseTypesEnum(str, Enum):
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

class ResourceTypeTypesEnum(str, Enum):
    CONSTANT = "CONSTANT"
    TEMPORAL = "TEMPORAL"

class ResourceTypeRequest(BaseModel):
    id: Optional[int] = None
    name: str
    type: ResourceTypeTypesEnum
    attributes: List[ResourceTypeAttributeRequest]


class IMResourceTypesServiceSyntax :
    @staticmethod
    async def handle_syntax_mistakes(user_id: int, data: Dict[str, Any]):
        try:
            # если ошибок нет, возвращаем проверенные данные
            validated_data = ResourceTypeRequest(**data)
            return validated_data
        
        except ValidationError as e:
            syntax_mistakes = []

            for error in e.errors():
                field = " -> ".join(map(str, error.get("loc", ["unknown"])))
                message = error.get("msg", "Ошибка валидации")
                syntax_mistakes.append(f"Ошибка в поле '{field}': {message}")

            for mistake in syntax_mistakes:
                print(mistake) # ??

            raise e 
        

    def process_tip(exception: str) -> str:
        ...
