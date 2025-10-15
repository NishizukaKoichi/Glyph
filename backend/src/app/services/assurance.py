"""Assurance score calculation service."""
from datetime import UTC, datetime
from typing import Literal

from app.core.config import settings
from app.models.auth_factor import AuthFactor

# Factor weights according to spec
FACTOR_WEIGHTS = {
    "webauthn": 35,
    "google": 25,
    "microsoft": 25,
    "github": 15,
    "x": 15,
    "verified_email": 10,
    "kyc": 40,
}


class AssuranceCalculator:
    """Calculate assurance scores for users."""

    def __init__(self):
        """Initialize assurance calculator."""
        self.level_alpha = settings.assurance_level_alpha
        self.level_beta = settings.assurance_level_beta
        self.level_gamma = settings.assurance_level_gamma

    def calculate_score(
        self, auth_factors: list[AuthFactor]
    ) -> tuple[int, Literal["alpha", "beta", "gamma"]]:
        """Calculate assurance score from authentication factors.

        Args:
            auth_factors: List of user's authentication factors

        Returns:
            Tuple of (score, level)
        """
        if not auth_factors:
            return 0, "alpha"

        total_score = 0
        factor_types = []
        most_recent_auth = None

        for factor in auth_factors:
            # Get base weight
            weight = FACTOR_WEIGHTS.get(factor.factor_type, 0)

            # Apply independence factor
            weight *= factor.independence_factor

            # Apply freshness factor
            if factor.last_used_at:
                days_since = (datetime.now(UTC) - factor.last_used_at).days
                freshness = self._calculate_freshness(days_since)
                weight *= freshness

                # Track most recent
                if most_recent_auth is None or factor.last_used_at > most_recent_auth:
                    most_recent_auth = factor.last_used_at

            total_score += weight
            factor_types.append(factor.factor_type)

        # Determine level
        level = self._determine_level(
            int(total_score), factor_types, most_recent_auth
        )

        return int(total_score), level

    def _calculate_freshness(self, days_since: int) -> float:
        """Calculate freshness multiplier based on days since last use.

        Args:
            days_since: Days since factor was last used

        Returns:
            Freshness multiplier (0.0 to 1.0)
        """
        if days_since <= 1:
            return 1.0
        if days_since <= 7:
            return 0.95
        if days_since <= 30:
            return 0.85
        if days_since <= 90:
            return 0.7
        return 0.5

    def _determine_level(
        self,
        score: int,
        factor_types: list[str],
        most_recent_auth: datetime | None,
    ) -> Literal["alpha", "beta", "gamma"]:
        """Determine assurance level.

        Args:
            score: Calculated assurance score
            factor_types: List of factor types
            most_recent_auth: Most recent authentication timestamp

        Returns:
            Assurance level
        """
        # Gamma requires score >= 85 AND recent WebAuthn
        if score >= self.level_gamma:
            if "webauthn" in factor_types and most_recent_auth:
                days_since = (datetime.now(UTC) - most_recent_auth).days
                if days_since <= 30:  # WebAuthn used within 30 days
                    return "gamma"

        # Beta requires score >= 70
        if score >= self.level_beta:
            return "beta"

        # Alpha is default (score >= 40)
        return "alpha"

    def get_freshness_days(self, auth_factors: list[AuthFactor]) -> int:
        """Get days since most recent authentication.

        Args:
            auth_factors: List of user's authentication factors

        Returns:
            Days since most recent authentication
        """
        if not auth_factors:
            return 999

        most_recent = None
        for factor in auth_factors:
            if factor.last_used_at:
                if most_recent is None or factor.last_used_at > most_recent:
                    most_recent = factor.last_used_at

        if most_recent is None:
            return 999

        return (datetime.now(UTC) - most_recent).days
