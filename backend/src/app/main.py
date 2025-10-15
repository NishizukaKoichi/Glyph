"""
Main application entry point for Glyph authentication broker.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("🔮 Glyph is starting...")
    yield
    # Shutdown
    print("🔮 Glyph is shutting down...")


app = FastAPI(
    title=settings.app_name,
    description="Glyph — 刻まれた印章が、本人性と信頼を運ぶ",
    version=settings.app_version,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    message: str
    version: str


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "Glyph — 刻まれた印章が、本人性と信頼を運ぶ",
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="healthy", message="Glyph is running", version=settings.app_version
    )


# OIDC Discovery endpoint
@app.get("/.well-known/openid-configuration")
async def oidc_discovery() -> dict:
    """OpenID Connect discovery endpoint."""
    return {
        "issuer": "https://glyph.id",
        "authorization_endpoint": "https://glyph.id/authorize",
        "token_endpoint": "https://glyph.id/token",
        "userinfo_endpoint": "https://glyph.id/userinfo",
        "jwks_uri": "https://glyph.id/.well-known/jwks.json",
        "response_types_supported": ["code"],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": ["HS256", "RS256"],
        "scopes_supported": ["openid", "profile", "email"],
        "token_endpoint_auth_methods_supported": ["client_secret_post"],
        "claims_supported": [
            "sub",
            "email",
            "email_verified",
            "aegis_assurance",
            "extensions",
        ],
    }


# Demo endpoint for token generation (will be replaced with OAuth flow)
@app.get("/api/v1/demo/token")
async def demo_token() -> dict:
    """Demo endpoint showing Glyph token structure."""
    return {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer",
        "aegis_assurance": {
            "score": 76,
            "level": "beta",
            "factors": ["webauthn", "google"],
            "freshness_days": 18,
        },
        "extensions": {
            "trust_signals": {
                "risk": {
                    "score": 24,
                    "band": "low",
                    "updated_at": "2025-10-15T00:00:00Z",
                    "ttl_sec": 604800,
                },
                "provenance": [
                    {
                        "issuer": "https://srv-a.example.com",
                        "kind": "block",
                        "count": 3,
                        "since": "2025-08-14T12:00:00Z",
                        "jws": "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9...",
                        "expires_at": "2025-11-14T12:00:00Z",
                        "weight": 0.9,
                    }
                ],
            }
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
