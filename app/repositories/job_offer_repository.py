from sqlalchemy.orm import Session

from app import models


def get_existing(
    db: Session,
    *,
    company_id: int,
    title: str,
    description: str,
) -> models.JobOffer | None:
    return (
        db.query(models.JobOffer)
        .filter(
            models.JobOffer.company_id == company_id,
            models.JobOffer.title == title,
            models.JobOffer.description == description,
        )
        .first()
    )


def create(
    db: Session,
    *,
    company_id: int,
    title: str,
    description: str,
) -> models.JobOffer:
    job_offer = models.JobOffer(
        company_id=company_id,
        title=title,
        description=description,
    )
    db.add(job_offer)
    db.flush()
    return job_offer


def get_or_create(
    db: Session,
    *,
    company_id: int,
    title: str,
    description: str,
) -> models.JobOffer:
    job_offer = get_existing(
        db,
        company_id=company_id,
        title=title,
        description=description,
    )
    if job_offer:
        return job_offer
    return create(db, company_id=company_id, title=title, description=description)
