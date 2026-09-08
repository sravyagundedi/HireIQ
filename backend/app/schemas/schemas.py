from pydantic import BaseModel, ConfigDict, Field
from typing import Any


class CandidateCreate(BaseModel):
    name: str
    email: str


class CandidateOut(CandidateCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class InterviewCreate(BaseModel):
    candidate_id: int
    title: str = "AI Interview"


class InterviewOut(BaseModel):
    id: int
    candidate_id: int
    title: str
    status: str
    overall_score: float | None = None
    recommendation: str | None = None
    model_config = ConfigDict(from_attributes=True)


class QuestionOut(BaseModel):
    id: int
    text: str
    question_type: str
    order_index: int
    model_config = ConfigDict(from_attributes=True)


class InterviewStartOut(BaseModel):
    interview: InterviewOut
    session_id: int
    questions: list[QuestionOut]


class EvaluationResult(BaseModel):
    score: float = Field(ge=0, le=10)
    criteria_scores: dict[str, float] = Field(default_factory=dict)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    recommendation: str
    rationale: str = ""


class EvaluationOut(EvaluationResult):
    keywords: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    sentiment: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0, le=100)


class ResponseStatus(BaseModel):
    response_id: int
    status: str
    transcript: str | None = None
    evaluation: EvaluationOut | None = None
