import json
from typing import Protocol

from sqlalchemy.orm import Session

from app import models


class AnalysisLike(Protocol):
    fit_score: float
    similarity_score: float
    skill_coverage: float
    matched_keywords: list[str]
    missing_keywords: list[str]
    recommendations: list[str]
    outreach_message: str


def create_for_application(
    db: Session,
    *,
    application: models.JobApplication,
    analysis: AnalysisLike,
) -> models.AnalysisResult:
    result = models.AnalysisResult(
        fit_score=analysis.fit_score,
        similarity_score=analysis.similarity_score,
        skill_coverage=analysis.skill_coverage,
        matched_keywords=json.dumps(analysis.matched_keywords),
        missing_keywords=json.dumps(analysis.missing_keywords),
        recommendations=json.dumps(analysis.recommendations),
        outreach_message=analysis.outreach_message,
    )
    application.analysis_result = result
    db.add(result)
    db.flush()
    return result
