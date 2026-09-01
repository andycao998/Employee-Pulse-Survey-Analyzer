""" Models for surveys and responses as well as DTOs for their transformations (create and update) """

from pydantic import BaseModel, ConfigDict, Field, model_validator
from datetime import date, datetime, timezone
from typing import Literal
from typing_extensions import Self
from employee_survey_analyzer.representations import SurveyInvalidDateRangeError

# ======================== SURVEY MODELS ========================


class Survey(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    prompt: str = Field(min_length=12) # shortest open prompt: "How are you?"
    department: str
    open_date: date
    close_date: date

    # validate against impossible date range
    @model_validator(mode='after')
    def validate_dates(self) -> Self:
        if self.close_date < self.open_date:
            raise SurveyInvalidDateRangeError(code="UNPROCESSABLE_CONTENT", 
                                                  status=422, 
                                                  detail="close_date cannot be before open_date")
        
        return self


class CreateSurveyDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    prompt: str = Field(min_length=12)
    department: str
    open_date: date
    close_date: date


class UpdateSurveyDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # only allow editing of title, prompt, and close_date
    title: str
    prompt: str = Field(min_length=12)
    close_date: date


# ======================== RESPONSE MODELS ========================

Sentiment = Literal["NEUTRAL", "POSITIVE", "NEGATIVE", "MIXED"]

class Response(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    body: str = Field(min_length=15, frozen=True) # extra validation for response immutability
    survey_id: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sentiment: Sentiment
    confidence_score: float


class CreateResponseDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    body: str = Field(frozen=True)
    survey_id: int
    sentiment: Sentiment
    confidence_score: float