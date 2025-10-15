"""Authentication factor model."""
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class AuthFactor(Base):
    """Authentication factor model for tracking user authentication methods."""

    __tablename__ = "auth_factors"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )

    # Factor details
    factor_type: Mapped[str] = mapped_column(String(50), nullable=False)  # webauthn, google, etc.
    provider: Mapped[str | None] = mapped_column(String(100))  # OAuth provider name
    provider_user_id: Mapped[str | None] = mapped_column(String(255))  # Provider's user ID

    # Weights for score calculation
    base_weight: Mapped[int] = mapped_column(Integer, default=0)  # Base score weight
    independence_factor: Mapped[float] = mapped_column(default=1.0)  # Independence multiplier

    # Additional data
    extra_data: Mapped[dict] = mapped_column(JSON, default=dict)  # Additional factor data

    # Timestamps
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="auth_factors")
