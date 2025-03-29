from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class RelevantResourceRequest(BaseModel):
    id: Optional[int] = None
    name: str
    resource_type_id: int


class RelevantResourceResponse(RelevantResourceRequest):
    id: int


class TemplateTypeEnum(str, Enum):
    IRREGULAR_EVENT = "IRREGULAR_EVENT"
    OPERATION = "OPERATION"
    RULE = "RULE"


class TemplateMetaRequest(BaseModel):
    id: Optional[int] = None
    name: str
    type: TemplateTypeEnum
    rel_resources: List[RelevantResourceRequest]


class TemplateMetaResponse(TemplateMetaRequest):
    id: int
    rel_resources: List[RelevantResourceResponse]


class OperationBody(BaseModel):
    condition: str
    body_before: str
    delay: int
    body_after: str


class OperationRequest(BaseModel):
    meta: TemplateMetaRequest
    body: OperationBody


class OperationResponse(OperationRequest):
    meta: TemplateMetaResponse


class RuleBody(BaseModel):
    condition: str
    body: str


class RuleRequest(BaseModel):
    meta: TemplateMetaRequest
    body: RuleBody


class RuleResponse(RuleRequest):
    meta: TemplateMetaResponse


class IrregularEventBody(BaseModel):
    body: str


class GeneratorTypeEnum(str, Enum):
    NORMAL = "NORMAL"
    PRECISE = "PRECISE"
    UNIFORM = "UNIFORM"
    EXPONENTIAL = "EXPONENTIAL"
    GAUSSIAN = "GAUSSIAN"
    POISSON = "POISSON"


class IrregularEventGenerator(BaseModel):
    type: GeneratorTypeEnum
    value: float
    dispersion: float


class IrregularEventRequest(BaseModel):
    meta: TemplateMetaRequest
    generator: IrregularEventGenerator
    body: IrregularEventBody


class IrregularEventResponse(IrregularEventRequest):
    meta: TemplateMetaResponse


