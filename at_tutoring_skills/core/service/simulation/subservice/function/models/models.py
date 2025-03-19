from typing import Optional, Sequence

from pydantic import BaseModel


class FunctionParameterRequest(BaseModel):
    id: Optional[int] = None
    name: str
    type: str


class FunctionRequest(BaseModel):
    id: Optional[int] = None
    name: str
    ret_type: str
    body: str
    params: Sequence[FunctionParameterRequest]


class FunctionParameterResponse(FunctionParameterRequest):
    id: int


class FunctionResponse(FunctionRequest):
    id: int
    params: Sequence[FunctionParameterResponse]
