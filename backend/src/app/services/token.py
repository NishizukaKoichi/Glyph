"""Token generation service integrating assurance and trust."""
from datetime import UTC, datetime

from app.core.security import create_access_token, create_refresh_token
from app.models.auth_factor import AuthFactor
from app.models.trust_signal import TrustSignal
from app.models.user import User
from app.schemas.token import (
    AssuranceScore,
    GlyphToken,
    Token,
    TrustProvenance,
    TrustRisk,
    TrustSignals,
)
from app.services.assurance import AssuranceCalculator
from app.services.trust import TrustCalculator


class TokenService:
    """Service for generating Glyph tokens with assurance and trust signals."""

    def __init__(self):
        """Initialize token service."""
        self.assurance_calc = AssuranceCalculator()
        self.trust_calc = TrustCalculator()

    async def generate_glyph_token(
        self,
        user: User,
        auth_factors: list[AuthFactor],
        trust_signals: list[TrustSignal],
    ) -> Token:
        """Generate a complete Glyph token with assurance and trust signals.

        Args:
            user: User model
            auth_factors: User's authentication factors
            trust_signals: User's trust signals

        Returns:
            Token with access and refresh tokens
        """
        # Calculate assurance score
        score, level = self.assurance_calc.calculate_score(auth_factors)
        freshness_days = self.assurance_calc.get_freshness_days(auth_factors)

        assurance = AssuranceScore(
            score=score,
            level=level,
            factors=[f.factor_type for f in auth_factors],
            freshness_days=freshness_days,
        )

        # Calculate trust risk
        risk_score, risk_band = self.trust_calc.calculate_risk_score(trust_signals)

        # Filter consented signals
        consented_signals = self.trust_calc.filter_by_consent(trust_signals)

        # Build trust risk
        trust_risk = TrustRisk(
            score=risk_score,
            band=risk_band,
            updated_at=datetime.now(UTC).isoformat(),
            ttl_sec=604800,  # 7 days
        )

        # Build provenance list
        provenance = []
        for signal in consented_signals[:10]:  # Limit to top 10
            if signal.expires_at and signal.since:
                prov = TrustProvenance(
                    issuer=signal.issuer,
                    kind=signal.kind,
                    count=signal.count,
                    since=signal.since.isoformat(),
                    jws=signal.jws or "",
                    expires_at=signal.expires_at.isoformat(),
                    weight=signal.weight,
                )
                provenance.append(prov)

        # Build trust signals
        trust = TrustSignals(
            risk=trust_risk,
            provenance=provenance,
            consent={
                "granted": True,
                "scope": {"block": {"share": True}, "mute": {"share": False}},
                "retention": {"max_age_days": 180, "auto_decay": True},
            },
            policy={
                "decay": {"half_life_days": 90, "min_factor": 0.15},
                "caps": {"issuer_daily_max": 50},
                "appeals_url": "https://glyph.id/appeals",
            },
            transparency={
                "receipts_endpoint": "https://glyph.id/me/trust/receipts",
                "explain_url": "https://glyph.id/me/trust/explain",
            },
            legal={
                "disclaimer_url": "https://glyph.id/legal/trust-disclaimer",
                "indemnification": True,
                "liability_cap": "signals-are-advisory",
            },
        )

        # Build complete Glyph token
        glyph_token = GlyphToken(
            aegis_assurance=assurance,
            extensions={"trust_signals": trust.model_dump()},
        )

        # Create JWT payload
        token_data = {
            "sub": user.id,
            "email": user.email,
            "aegis_assurance": assurance.model_dump(),
            "extensions": {"trust_signals": trust.model_dump()},
        }

        # Generate access and refresh tokens
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token({"sub": user.id})

        return Token(access_token=access_token, refresh_token=refresh_token)
