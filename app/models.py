from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum as SqlEnum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class ApplicationStatus(str, enum.Enum):
    saved = "saved"
    applied = "applied"
    interview = "interview"
    rejected = "rejected"
    offer = "offer"


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    job_offers: Mapped[list["JobOffer"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )


class JobOffer(Base):
    __tablename__ = "job_offers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    company: Mapped["Company"] = relationship(
        back_populates="job_offers",
    )

    applications: Mapped[list["JobApplication"]] = relationship(
        back_populates="job_offer",
        cascade="all, delete-orphan",
    )


class JobApplication(Base):
    __tablename__ = "job_applications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_offer_id: Mapped[int] = mapped_column(
        ForeignKey("job_offers.id"),
        nullable=False,
        index=True,
    )

    status: Mapped[ApplicationStatus] = mapped_column(
        SqlEnum(ApplicationStatus, name="application_status"),
        default=ApplicationStatus.saved,
        nullable=False,
    )

    cv_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    job_offer: Mapped["JobOffer"] = relationship(
        back_populates="applications",
    )

    analysis_result: Mapped["AnalysisResult"] = relationship(
        back_populates="application",
        cascade="all, delete-orphan",
        single_parent=True,
    )


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    application_id: Mapped[int] = mapped_column(
        ForeignKey("job_applications.id"),
        unique=True,
        nullable=False,
    )

    fit_score: Mapped[float] = mapped_column(Float, nullable=False)
    similarity_score: Mapped[float] = mapped_column(Float, nullable=False)
    skill_coverage: Mapped[float] = mapped_column(Float, nullable=False)

    matched_keywords: Mapped[str] = mapped_column(Text, default="", nullable=False)
    missing_keywords: Mapped[str] = mapped_column(Text, default="", nullable=False)
    recommendations: Mapped[str] = mapped_column(Text, default="", nullable=False)
    outreach_message: Mapped[str] = mapped_column(Text, default="", nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    application: Mapped["JobApplication"] = relationship(
        back_populates="analysis_result",
    )
