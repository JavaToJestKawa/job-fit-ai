from sqlalchemy.orm import Session, joinedload

from app import models


def _base_query(db: Session):
    return db.query(models.JobApplication).options(
        joinedload(models.JobApplication.job_offer).joinedload(models.JobOffer.company),
        joinedload(models.JobApplication.analysis_result),
    )


def create(
    db: Session,
    *,
    job_offer_id: int,
    cv_text: str,
) -> models.JobApplication:
    application = models.JobApplication(job_offer_id=job_offer_id, cv_text=cv_text)
    db.add(application)
    db.flush()
    return application


def get_by_id(db: Session, application_id: int) -> models.JobApplication | None:
    return db.query(models.JobApplication).filter(models.JobApplication.id == application_id).first()


def get_with_details(db: Session, application_id: int) -> models.JobApplication | None:
    return _base_query(db).filter(models.JobApplication.id == application_id).first()


def list_with_details(db: Session) -> list[models.JobApplication]:
    return _base_query(db).order_by(models.JobApplication.created_at.desc()).all()


def update_status(
    db: Session,
    *,
    application: models.JobApplication,
    status: models.ApplicationStatus,
) -> models.JobApplication:
    application.status = status
    db.flush()
    return application


def delete(db: Session, *, application: models.JobApplication) -> None:
    db.delete(application)
    db.flush()
