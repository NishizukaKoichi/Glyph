"""WebAuthn/Passkey authentication endpoints."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.services.token import TokenService
from app.services.user import UserService
from app.services.webauthn import WebAuthnService

router = APIRouter(prefix="/auth/webauthn", tags=["webauthn"])
webauthn_service = WebAuthnService()
user_service = UserService()
token_service = TokenService()

# In-memory challenge storage (should use Redis in production)
challenges: dict[str, str] = {}


class RegistrationStartRequest(BaseModel):
    """Request to start WebAuthn registration."""

    user_id: str
    username: str
    display_name: str


class RegistrationFinishRequest(BaseModel):
    """Request to finish WebAuthn registration."""

    user_id: str
    credential: dict[str, Any]
    challenge: str


class AuthenticationStartRequest(BaseModel):
    """Request to start WebAuthn authentication."""

    user_id: str


class AuthenticationFinishRequest(BaseModel):
    """Request to finish WebAuthn authentication."""

    user_id: str
    credential: dict[str, Any]
    challenge: str


@router.post("/register/start")
async def register_start(
    request: RegistrationStartRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Start WebAuthn registration.

    Args:
        request: Registration start request
        db: Database session

    Returns:
        Registration options for client
    """
    # Generate registration options
    options = webauthn_service.generate_registration_options(
        user_id=request.user_id,
        username=request.username,
        display_name=request.display_name,
    )

    # Store challenge temporarily
    challenge_id = str(uuid.uuid4())
    challenges[challenge_id] = options["challenge"]

    return {
        "challengeId": challenge_id,
        "options": options,
    }


@router.post("/register/finish")
async def register_finish(
    request: RegistrationFinishRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Finish WebAuthn registration.

    Args:
        request: Registration finish request
        db: Database session

    Returns:
        Success message
    """
    # Verify challenge exists
    if request.challenge not in challenges.values():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired challenge",
        )

    # Verify registration response
    try:
        verification = webauthn_service.verify_registration_response(
            credential=request.credential,
            expected_challenge=request.challenge,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration verification failed: {e!s}",
        ) from e

    if not verification["verified"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration verification failed",
        )

    # Store credential as auth factor
    await user_service.add_auth_factor(
        db,
        user_id=request.user_id,
        factor_type="webauthn",
        provider=None,
        provider_user_id=None,
        extra_data={
            "credential_id": verification["credential_id"],
            "credential_public_key": verification["credential_public_key"],
            "sign_count": verification["sign_count"],
            "aaguid": verification["aaguid"],
            "credential_device_type": verification["credential_device_type"],
            "credential_backed_up": verification["credential_backed_up"],
        },
    )

    # Clean up challenge
    for challenge_id, challenge in list(challenges.items()):
        if challenge == request.challenge:
            del challenges[challenge_id]
            break

    return {"status": "success", "message": "WebAuthn credential registered"}


@router.post("/authenticate/start")
async def authenticate_start(
    request: AuthenticationStartRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Start WebAuthn authentication.

    Args:
        request: Authentication start request
        db: Database session

    Returns:
        Authentication options for client
    """
    # Get user's WebAuthn credentials
    auth_factors = await user_service.get_user_auth_factors(db, request.user_id)
    webauthn_factors = [f for f in auth_factors if f.factor_type == "webauthn"]

    if not webauthn_factors:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No WebAuthn credentials found for user",
        )

    # Prepare credentials for authentication
    credentials = [
        {"credential_id": f.extra_data["credential_id"]} for f in webauthn_factors
    ]

    # Generate authentication options
    options = webauthn_service.generate_authentication_options(credentials)

    # Store challenge temporarily
    challenge_id = str(uuid.uuid4())
    challenges[challenge_id] = options["challenge"]

    return {
        "challengeId": challenge_id,
        "options": options,
    }


@router.post("/authenticate/finish")
async def authenticate_finish(
    request: AuthenticationFinishRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Finish WebAuthn authentication.

    Args:
        request: Authentication finish request
        db: Database session

    Returns:
        User info and Glyph token
    """
    # Verify challenge exists
    if request.challenge not in challenges.values():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired challenge",
        )

    # Get user and auth factors
    auth_factors = await user_service.get_user_auth_factors(db, request.user_id)
    webauthn_factors = [f for f in auth_factors if f.factor_type == "webauthn"]

    # Find matching credential
    credential_id = request.credential.get("rawId")
    matching_factor = None
    for factor in webauthn_factors:
        if factor.extra_data.get("credential_id") == credential_id:
            matching_factor = factor
            break

    if not matching_factor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credential not found",
        )

    # Verify authentication response
    try:
        verification = webauthn_service.verify_authentication_response(
            credential=request.credential,
            expected_challenge=request.challenge,
            credential_public_key=matching_factor.extra_data["credential_public_key"],
            credential_current_sign_count=matching_factor.extra_data["sign_count"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Authentication verification failed: {e!s}",
        ) from e

    if not verification["verified"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authentication verification failed",
        )

    # Update sign count
    matching_factor.extra_data["sign_count"] = verification["new_sign_count"]
    await user_service.add_auth_factor(
        db,
        user_id=request.user_id,
        factor_type="webauthn",
        provider=None,
        provider_user_id=None,
        extra_data=matching_factor.extra_data,
    )

    # Get user
    from app.models.user import User
    from sqlalchemy import select

    result = await db.execute(select(User).where(User.id == request.user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Get user's trust signals (empty for now)
    trust_signals = []  # TODO: Implement trust signals retrieval

    # Generate Glyph token
    glyph_token = await token_service.generate_glyph_token(
        user, auth_factors, trust_signals
    )

    # Clean up challenge
    for challenge_id, challenge in list(challenges.items()):
        if challenge == request.challenge:
            del challenges[challenge_id]
            break

    return {
        "status": "success",
        "user": {
            "id": user.id,
            "email": user.email,
            "email_verified": user.email_verified,
        },
        "token": glyph_token.model_dump(),
    }
