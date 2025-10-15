"""Token schemas."""
from pydantic import BaseModel, Field


class Token(BaseModel):
    """Token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""

    sub: str  # User ID
    type: str  # access or refresh
    exp: int  # Expiration timestamp


class AssuranceScore(BaseModel):
    """Assurance score in Glyph token."""

    score: int = Field(ge=0, le=100, description="Assurance score 0-100")
    level: str = Field(description="alpha, beta, or gamma")
    factors: list[str] = Field(description="List of authentication factors used")
    freshness_days: int = Field(
        ge=0, description="Days since most recent authentication"
    )


class TrustRisk(BaseModel):
    """Trust risk score."""

    score: int = Field(ge=0, le=100, description="Risk score 0-100")
    band: str = Field(description="low, medium, or high")
    updated_at: str = Field(description="ISO 8601 timestamp")
    ttl_sec: int = Field(description="Time to live in seconds")


class TrustProvenance(BaseModel):
    """Trust signal provenance."""

    issuer: str = Field(description="Issuer service URL")
    kind: str = Field(description="Signal kind: block, mute, etc")
    count: int = Field(ge=1, description="Number of signals")
    since: str = Field(description="ISO 8601 timestamp of first signal")
    jws: str = Field(description="JWS signature")
    expires_at: str = Field(description="ISO 8601 expiration timestamp")
    weight: float = Field(ge=0, le=1, description="Signal weight")


class TrustSignals(BaseModel):
    """Trust signals in Glyph token."""

    risk: TrustRisk
    provenance: list[TrustProvenance]
    consent: dict = Field(description="User consent configuration")
    policy: dict = Field(description="Trust policy configuration")
    transparency: dict = Field(description="Transparency endpoints")
    legal: dict = Field(description="Legal disclaimers")


class GlyphToken(BaseModel):
    """Complete Glyph token with assurance and trust signals."""

    aegis_assurance: AssuranceScore
    extensions: dict = Field(default_factory=lambda: {"trust_signals": {}})
