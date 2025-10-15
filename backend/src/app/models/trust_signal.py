"""Trust signal model."""
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class TrustSignal(Base):
    """Trust signal model for tracking user reputation signals."""

    __tablename__ = "trust_signals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )

    # Signal details
    issuer: Mapped[str] = mapped_column(String(255), nullable=False)  # Issuing service URL
    kind: Mapped[str] = mapped_column(String(50), nullable=False)  # block, mute, etc.
    count: Mapped[int] = mapped_column(Integer, default=1)  # Number of signals

    # Score calculation factors
    weight: Mapped[float] = mapped_column(Float, default=1.0)  # Signal weight
    independence_factor: Mapped[float] = mapped_column(Float, default=1.0)
    credibility: Mapped[float] = mapped_column(Float, default=1.0)  # Issuer credibility

    # JWS signature for verification
    jws: Mapped[str | None] = mapped_column(Text)  # Signed signal

    # User consent
    consent_granted: Mapped[bool] = mapped_column(default=False)
    consent_scope: Mapped[dict] = mapped_column(JSON, default=dict)

    # Additional data
    extra_data: Mapped[dict] = mapped_column(JSON, default=dict)

    # Timestamps
    since: Mapped[datetime] = mapped_column(DateTime(timezone=True))  # Signal start date
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="trust_signals")
