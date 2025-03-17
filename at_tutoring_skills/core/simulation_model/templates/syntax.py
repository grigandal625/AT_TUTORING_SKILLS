from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, ValidationError
from rest_framework import exceptions

# Определение моделей

class TemplateTypeEnum(str, Enum):
    IRREGULAR_EVENT = "IRREGULAR_EVENT"
    OPERATION = "OPERATION"
    RULE = "RULE"

class RelevantResourceRequest(BaseModel):
    id: Optional[int] = None
    name: str
    resource_type_id: int

class TemplateMetaRequest(BaseModel):
    id: Optional[int] = None
    name: str
    type: TemplateTypeEnum
    rel_resources: List[RelevantResourceRequest]

class OperationBody(BaseModel):
    condition: str
    body_before: str
    delay: int
    body_after: str

class OperationRequest(BaseModel):
    meta: TemplateMetaRequest
    body: OperationBody

class RuleBody(BaseModel):
    condition: str
    body: str

class RuleRequest(BaseModel):
    meta: TemplateMetaRequest
    body: RuleBody

class GeneratorTypeEnum(str, Enum):
    NORMAL = "NORMAL"
    PRECISE = "PRECISE"
    UNIFORM = "UNIFORM"
    EXPONENTIAL = "EXPONENTIAL"
    GAUSSIAN = "GAUSSIAN"
    POISSON = "POISSON"

class IrregularEventBody(BaseModel):
    body: str

class IrregularEventGenerator(BaseModel):
    type: GeneratorTypeEnum
    value: float
    dispersion: float

class IrregularEventRequest(BaseModel):
    meta: TemplateMetaRequest
    generator: IrregularEventGenerator
    body: IrregularEventBody

# Основной класс обработки синтаксических ошибок
class IMTemplateServiceSyntax:
    async def handle_syntax_mistakes(self, user_id: int, data: Dict[str, Any]):
        
        try:
            validated_data = self.validate_data(data)
            return await IMTemplateService.handle_syntax_mistakes(user_id, validated_data)

        except ValidationError as e:
            syntax_mistakes: List[str] = []

            for error in e.errors():
                field = ".".join(str(loc) for loc in error.get("loc", []))
                message = error.get("msg", "Invalid input")
                syntax_mistakes.append(f"Ошибка в поле '{field}': {message}")

            # Логирование ошибок (или сохранение в БД)
            for mistake in syntax_mistakes:
                self.repository.create_mistake(mistake)

            raise exceptions.ValidationError({"errors": syntax_mistakes})

    def validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        
        if "meta" not in data or "type" not in data["meta"]:
            raise ValueError("Отсутствует поле 'meta' или 'type'")

        template_type = data["meta"]["type"]

        if template_type == TemplateTypeEnum.IRREGULAR_EVENT:
            return IrregularEventRequest(**data).dict()

        elif template_type == TemplateTypeEnum.OPERATION:
            return OperationRequest(**data).dict()

        elif template_type == TemplateTypeEnum.RULE:
            return RuleRequest(**data).dict()

        else:
            raise ValueError(f"Неизвестный тип шаблона: {template_type}")
