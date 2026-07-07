from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.services import application_service

router = APIRouter(prefix="/api/applications", tags=["Applications"])


@router.post("/analyze", response_model=schemas.ApplicationRead, status_code=status.HTTP_201_CREATED)
def analyze_and_save_application(payload: schemas.ApplicationCreate, db: Session = Depends(get_db)):
    return application_service.create_analyzed_application(db, payload=payload)


@router.get("", response_model=list[schemas.ApplicationRead])
def get_applications(db: Session = Depends(get_db)):
    return application_service.list_applications(db)


@router.patch("/{application_id}/status", response_model=schemas.ApplicationRead)
def update_application_status(
    application_id: int,
    payload: schemas.ApplicationStatusUpdate,
    db: Session = Depends(get_db),
):
    updated_application = application_service.update_application_status(
        db,
        application_id=application_id,
        new_status=payload.status,
    )
    if updated_application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return updated_application


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(application_id: int, db: Session = Depends(get_db)):
    deleted = application_service.delete_application(db, application_id=application_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return None
