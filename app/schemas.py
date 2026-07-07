from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import ApplicationStatus


class ApplicationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company: str = Field(min_length=2, max_length=120, examples=["Allegro"])
    job_title: str = Field(min_length=2, max_length=160, examples=["Junior Backend Developer"])
    job_description: str = Field(min_length=40, examples=["We are looking for a junior Python developer..."])
    cv_text: str = Field(min_length=40, examples=["Computer Science student focused on ML and backend..."])


class ApplicationStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: ApplicationStatus


class CompanyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    website: str | None = None
    location: str | None = None
    created_at: datetime


class JobOfferRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    title: str
    description: str
    created_at: datetime


class AnalysisResultRead(BaseModel):
    fit_score: float
    similarity_score: float
    skill_coverage: float
    matched_keywords: list[str]
    missing_keywords: list[str]
    recommendations: list[str]
    outreach_message: str


class ApplicationRead(BaseModel):
    id: int
    status: ApplicationStatus
    created_at: datetime

    company_id: int
    company: str
    job_offer_id: int
    job_title: str
    job_description: str

    fit_score: float
    similarity_score: float
    skill_coverage: float
    matched_keywords: list[str]
    missing_keywords: list[str]
    recommendations: list[str]
    outreach_message: str
