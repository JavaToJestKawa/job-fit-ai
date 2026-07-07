from sqlalchemy.orm import Session

from app import models


def get_by_name(db: Session, name: str) -> models.Company | None:
    return db.query(models.Company).filter(models.Company.name == name).first()


def create(
    db: Session,
    *,
    name: str,
    website: str | None = None,
    location: str | None = None,
) -> models.Company:
    company = models.Company(name=name, website=website, location=location)
    db.add(company)
    db.flush()
    return company


def get_or_create(db: Session, *, name: str) -> models.Company:
    company = get_by_name(db, name)
    if company:
        return company
    return create(db, name=name)
