"""User management service."""
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth_factor import AuthFactor
from app.models.user import User
from app.services.assurance import FACTOR_WEIGHTS


class UserService:
    """Service for user management operations."""

    async def get_or_create_user(
        self,
        db: AsyncSession,
        email: str | None,
        email_verified: bool = False,
    ) -> User:
        """Get existing user or create new one.

        Args:
            db: Database session
            email: User email
            email_verified: Whether email is verified

        Returns:
            User model
        """
        # Try to find existing user by email
        if email:
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()

            if user:
                # Update email verification if needed
                if email_verified and not user.email_verified:
                    user.email_verified = email_verified
                    await db.commit()
                    await db.refresh(user)
                return user

        # Create new user
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            email_verified=email_verified,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def add_auth_factor(
        self,
        db: AsyncSession,
        user_id: str,
        factor_type: str,
        provider: str | None = None,
        provider_user_id: str | None = None,
        extra_data: dict | None = None,
    ) -> AuthFactor:
        """Add or update authentication factor for user.

        Args:
            db: Database session
            user_id: User ID
            factor_type: Factor type (google, microsoft, github, twitter, webauthn)
            provider: OAuth provider name
            provider_user_id: Provider's user ID
            extra_data: Additional factor data

        Returns:
            AuthFactor model
        """
        # Check if factor already exists
        result = await db.execute(
            select(AuthFactor).where(
                AuthFactor.user_id == user_id,
                AuthFactor.factor_type == factor_type,
                AuthFactor.provider == provider,
            )
        )
        factor = result.scalar_one_or_none()

        if factor:
            # Update existing factor
            factor.last_used_at = datetime.now(UTC)
            if provider_user_id:
                factor.provider_user_id = provider_user_id
            if extra_data:
                factor.extra_data = extra_data
        else:
            # Create new factor
            factor = AuthFactor(
                id=str(uuid.uuid4()),
                user_id=user_id,
                factor_type=factor_type,
                provider=provider,
                provider_user_id=provider_user_id,
                base_weight=FACTOR_WEIGHTS.get(factor_type, 0),
                independence_factor=1.0,
                extra_data=extra_data or {},
                last_used_at=datetime.now(UTC),
            )
            db.add(factor)

        await db.commit()
        await db.refresh(factor)
        return factor

    async def get_user_auth_factors(
        self, db: AsyncSession, user_id: str
    ) -> list[AuthFactor]:
        """Get all authentication factors for a user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List of AuthFactor models
        """
        result = await db.execute(
            select(AuthFactor).where(AuthFactor.user_id == user_id)
        )
        return list(result.scalars().all())
