from typing import List, Optional

from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from core.utils.strings import to_camel


class CamelModel(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class ErrorDetails(BaseModel):
    code: int = Field(example=1)
    message: str = Field(example="additional error message here")
    target: Optional[str] = Field(example="field_name")


class Error(BaseModel):
    code: int = Field(example=400)
    message: str = Field(example="main error message here")
    details: List[ErrorDetails]


class ErrorResponse(BaseModel):
    error: Error

    @staticmethod
    def create_response(status_code: int, message: str,
                        details: Optional[List[ErrorDetails]] = None):
        if details is None:
            details = []
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": status_code,
                    "message": message,
                    "details": details,
                }
            },
        )
