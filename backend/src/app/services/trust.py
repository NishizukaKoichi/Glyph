"""Trust signals calculation service."""
from datetime import UTC, datetime
from typing import Literal

from app.models.trust_signal import TrustSignal

# Signal weights according to spec
SIGNAL_WEIGHTS = {
    "block": 1.0,
    "mute": 0.4,
}


class TrustCalculator:
    """Calculate trust risk scores for users."""

    def __init__(self):
        """Initialize trust calculator."""
        self.half_life_days = 90  # Freshness half-life
        self.min_freshness_factor = 0.15  # Minimum freshness multiplier

    def calculate_risk_score(
        self, trust_signals: list[TrustSignal]
    ) -> tuple[int, Literal["low", "medium", "high"]]:
        """Calculate trust risk score from signals.

        Args:
            trust_signals: List of user's trust signals

        Returns:
            Tuple of (risk_score, risk_band)
        """
        if not trust_signals:
            return 0, "low"

        # Filter to consented signals only
        consented_signals = [s for s in trust_signals if s.consent_granted]

        if not consented_signals:
            return 0, "low"

        total_risk = 0.0

        for signal in consented_signals:
            # Get base weight
            base_weight = SIGNAL_WEIGHTS.get(signal.kind, 0.5)

            # Apply signal-specific weight
            weighted = base_weight * signal.weight

            # Apply independence factor
            weighted *= signal.independence_factor

            # Apply freshness decay
            if signal.since:
                days_old = (datetime.now(UTC) - signal.since).days
                freshness = self._calculate_freshness_decay(days_old)
                weighted *= freshness

            # Apply issuer credibility
            weighted *= signal.credibility

            # Multiply by count (number of signals from same issuer)
            weighted *= signal.count

            total_risk += weighted

        # Convert to 0-100 scale and determine band
        risk_score = int(min(total_risk * 10, 100))  # Scale to 0-100
        risk_band = self._determine_risk_band(risk_score)

        return risk_score, risk_band

    def _calculate_freshness_decay(self, days_old: int) -> float:
        """Calculate freshness decay factor using half-life.

        Args:
            days_old: Days since signal was issued

        Returns:
            Freshness multiplier (min_freshness_factor to 1.0)
        """
        if days_old <= 0:
            return 1.0

        # Exponential decay with half-life
        decay = 0.5 ** (days_old / self.half_life_days)

        # Apply minimum floor
        return max(decay, self.min_freshness_factor)

    def _determine_risk_band(
        self, risk_score: int
    ) -> Literal["low", "medium", "high"]:
        """Determine risk band from score.

        Uses conservative thresholds to minimize false positives.

        Args:
            risk_score: Calculated risk score (0-100)

        Returns:
            Risk band
        """
        # Conservative thresholds to prevent false bans
        if risk_score >= 70:
            return "high"
        if risk_score >= 30:
            return "medium"
        return "low"

    def filter_by_consent(
        self, trust_signals: list[TrustSignal], issuer: str | None = None
    ) -> list[TrustSignal]:
        """Filter trust signals by user consent.

        Args:
            trust_signals: List of trust signals
            issuer: Optional issuer filter

        Returns:
            Filtered list of consented signals
        """
        filtered = []

        for signal in trust_signals:
            if not signal.consent_granted:
                continue

            # Check issuer-specific consent
            if issuer:
                consent_scope = signal.consent_scope or {}
                signal_kind_scope = consent_scope.get(signal.kind, {})

                # Check if this issuer is allowed
                if isinstance(signal_kind_scope, dict):
                    if not signal_kind_scope.get("share", False):
                        continue

                    allowed_issuers = signal_kind_scope.get("issuers", [])
                    if allowed_issuers and issuer not in allowed_issuers:
                        continue

            filtered.append(signal)

        return filtered

    def should_auto_decay(self, signal: TrustSignal, retention_days: int) -> bool:
        """Check if signal should be auto-decayed based on retention policy.

        Args:
            signal: Trust signal to check
            retention_days: Maximum retention days from policy

        Returns:
            True if signal should be decayed/removed
        """
        if not signal.since:
            return False

        days_old = (datetime.now(UTC) - signal.since).days
        return days_old > retention_days
