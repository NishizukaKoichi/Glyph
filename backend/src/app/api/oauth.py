"""OAuth authentication endpoints."""
from typing import Literal

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.services.oauth import OAuthService
from app.services.token import TokenService
from app.services.user import UserService

router = APIRouter(prefix="/auth", tags=["oauth"])
oauth_service = OAuthService()
user_service = UserService()
token_service = TokenService()


@router.get("/login/{provider}")
async def login(
    request: Request,
    provider: Literal["google", "microsoft", "github", "twitter"],
) -> RedirectResponse:
    """Initiate OAuth login flow.

    Args:
        request: FastAPI request
        provider: OAuth provider name

    Returns:
        Redirect to provider's authorization page
    """
    redirect_uri = request.url_for("auth_callback", provider=provider)
    return await oauth_service.oauth.create_client(provider).authorize_redirect(
        request, redirect_uri
    )


@router.get("/callback/{provider}")
async def auth_callback(
    request: Request,
    provider: Literal["google", "microsoft", "github", "twitter"],
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Handle OAuth callback.

    Args:
        request: FastAPI request
        provider: OAuth provider name
        db: Database session

    Returns:
        User info and Glyph token
    """
    # Get access token
    token = await oauth_service.oauth.create_client(provider).authorize_access_token(
        request
    )

    # Get user info based on provider
    if provider == "google":
        user_info = await oauth_service.get_user_info_google(token)
    elif provider == "microsoft":
        user_info = await oauth_service.get_user_info_microsoft(token)
    elif provider == "github":
        user_info = await oauth_service.get_user_info_github(token)
    elif provider == "twitter":
        user_info = await oauth_service.get_user_info_twitter(token)
    else:
        return {"error": "Unsupported provider"}

    # Get or create user
    user = await user_service.get_or_create_user(
        db,
        email=user_info.get("email"),
        email_verified=user_info.get("email_verified", False),
    )

    # Add or update auth factor
    await user_service.add_auth_factor(
        db,
        user_id=user.id,
        factor_type=provider,
        provider=provider,
        provider_user_id=user_info.get("provider_user_id"),
        extra_data={
            "name": user_info.get("name"),
            "picture": user_info.get("picture"),
            "username": user_info.get("username"),
            "verified": user_info.get("verified", False),
        },
    )

    # Get all user's auth factors
    auth_factors = await user_service.get_user_auth_factors(db, user.id)

    # Get user's trust signals (empty for now)
    trust_signals = []  # TODO: Implement trust signals retrieval

    # Generate Glyph token
    glyph_token = await token_service.generate_glyph_token(
        user, auth_factors, trust_signals
    )

    return {
        "status": "success",
        "provider": provider,
        "user": {
            "id": user.id,
            "email": user.email,
            "email_verified": user.email_verified,
        },
        "token": glyph_token.model_dump(),
    }
