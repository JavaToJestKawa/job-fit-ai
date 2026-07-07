import json

from sqlalchemy.orm import Session

from app import models, schemas
from app.repositories import analysis_repository, application_repository, company_repository, job_offer_repository
from app.services.analyzer import analyze_application


def _loads_list(value: str) -> list[str]:
    if not value:
        return []
    try:
        loaded = json.loads(value)
    except json.JSONDecodeError:
        return []
    return loaded if isinstance(loaded, list) else []


def to_application_read(application: models.JobApplication) -> schemas.ApplicationRead:
    job_offer = application.job_offer
    company = job_offer.company
    analysis = application.analysis_result

    return schemas.ApplicationRead(
        id=application.id,
        status=application.status,
        created_at=application.created_at,
        company_id=company.id,
        company=company.name,
        job_offer_id=job_offer.id,
        job_title=job_offer.title,
        job_description=job_offer.description,
        fit_score=analysis.fit_score,
        similarity_score=analysis.similarity_score,
        skill_coverage=analysis.skill_coverage,
        matched_keywords=_loads_list(analysis.matched_keywords),
        missing_keywords=_loads_list(analysis.missing_keywords),
        recommendations=_loads_list(analysis.recommendations),
        outreach_message=analysis.outreach_message,
    )


def create_analyzed_application(
    db: Session,
    *,
    payload: schemas.ApplicationCreate,
) -> schemas.ApplicationRead:
    company_name = payload.company.strip()
    job_title = payload.job_title.strip()
    job_description = payload.job_description.strip()
    cv_text = payload.cv_text.strip()

    analysis = analyze_application(
        company=company_name,
        job_title=job_title,
        cv_text=cv_text,
        job_description=job_description,
    )

    company = company_repository.get_or_create(db, name=company_name)
    job_offer = job_offer_repository.get_or_create(
        db,
        company_id=company.id,
        title=job_title,
        description=job_description,
    )
    application = application_repository.create(
        db,
        job_offer_id=job_offer.id,
        cv_text=cv_text,
    )
    analysis_repository.create_for_application(
        db,
        application=application,
        analysis=analysis,
    )

    db.commit()

    saved_application = application_repository.get_with_details(db, application.id)
    return to_application_read(saved_application)


def list_applications(db: Session) -> list[schemas.ApplicationRead]:
    applications = application_repository.list_with_details(db)
    return [to_application_read(application) for application in applications]


def update_application_status(
    db: Session,
    *,
    application_id: int,
    new_status: models.ApplicationStatus,
) -> schemas.ApplicationRead | None:
    application = application_repository.get_by_id(db, application_id)
    if application is None:
        return None

    application_repository.update_status(db, application=application, status=new_status)
    db.commit()

    updated_application = application_repository.get_with_details(db, application_id)
    return to_application_read(updated_application)


def delete_application(db: Session, *, application_id: int) -> bool:
    application = application_repository.get_by_id(db, application_id)
    if application is None:
        return False

    application_repository.delete(db, application=application)
    db.commit()
    return True
