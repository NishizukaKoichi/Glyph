"""OAuth provider service for external IdP integration."""
from typing import Any

import httpx
from authlib.integrations.starlette_client import OAuth

from app.core.config import settings

# Initialize OAuth client
oauth = OAuth()

# Register Google OAuth
if settings.google_client_id and settings.google_client_secret:
    oauth.register(
        name="google",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

# Register Microsoft OAuth
if settings.microsoft_client_id and settings.microsoft_client_secret:
    oauth.register(
        name="microsoft",
        client_id=settings.microsoft_client_id,
        client_secret=settings.microsoft_client_secret,
        server_metadata_url="https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

# Register GitHub OAuth
if settings.github_client_id and settings.github_client_secret:
    oauth.register(
        name="github",
        client_id=settings.github_client_id,
        client_secret=settings.github_client_secret,
        authorize_url="https://github.com/login/oauth/authorize",
        access_token_url="https://github.com/login/oauth/access_token",
        api_base_url="https://api.github.com/",
        client_kwargs={"scope": "read:user user:email"},
    )

# Register X (Twitter) OAuth 2.0
if settings.x_client_id and settings.x_client_secret:
    oauth.register(
        name="twitter",
        client_id=settings.x_client_id,
        client_secret=settings.x_client_secret,
        authorize_url="https://twitter.com/i/oauth2/authorize",
        access_token_url="https://api.twitter.com/2/oauth2/token",
        api_base_url="https://api.twitter.com/2/",
        client_kwargs={
            "scope": "tweet.read users.read",
            "token_endpoint_auth_method": "client_secret_post",
        },
    )


class OAuthService:
    """Service for handling OAuth provider operations."""

    def __init__(self):
        """Initialize OAuth service."""
        self.oauth = oauth

    async def get_user_info_google(self, token: dict[str, Any]) -> dict[str, Any]:
        """Get user info from Google.

        Args:
            token: OAuth token dict

        Returns:
            User info dict with email, name, picture, email_verified
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {token['access_token']}"},
            )
            response.raise_for_status()
            user_info = response.json()

            return {
                "provider": "google",
                "provider_user_id": user_info["id"],
                "email": user_info.get("email"),
                "email_verified": user_info.get("verified_email", False),
                "name": user_info.get("name"),
                "picture": user_info.get("picture"),
            }

    async def get_user_info_microsoft(self, token: dict[str, Any]) -> dict[str, Any]:
        """Get user info from Microsoft.

        Args:
            token: OAuth token dict

        Returns:
            User info dict
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://graph.microsoft.com/v1.0/me",
                headers={"Authorization": f"Bearer {token['access_token']}"},
            )
            response.raise_for_status()
            user_info = response.json()

            return {
                "provider": "microsoft",
                "provider_user_id": user_info["id"],
                "email": user_info.get("mail") or user_info.get("userPrincipalName"),
                "email_verified": True,  # Microsoft accounts are verified
                "name": user_info.get("displayName"),
                "picture": None,  # Would need separate call
            }

    async def get_user_info_github(self, token: dict[str, Any]) -> dict[str, Any]:
        """Get user info from GitHub.

        Args:
            token: OAuth token dict

        Returns:
            User info dict
        """
        async with httpx.AsyncClient() as client:
            # Get user profile
            response = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {token['access_token']}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )
            response.raise_for_status()
            user_info = response.json()

            # Get primary email
            email_response = await client.get(
                "https://api.github.com/user/emails",
                headers={
                    "Authorization": f"Bearer {token['access_token']}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )
            email_response.raise_for_status()
            emails = email_response.json()

            primary_email = next(
                (e for e in emails if e.get("primary")),
                emails[0] if emails else {},
            )

            return {
                "provider": "github",
                "provider_user_id": str(user_info["id"]),
                "email": primary_email.get("email"),
                "email_verified": primary_email.get("verified", False),
                "name": user_info.get("name") or user_info.get("login"),
                "picture": user_info.get("avatar_url"),
            }

    async def get_user_info_twitter(self, token: dict[str, Any]) -> dict[str, Any]:
        """Get user info from X (Twitter).

        Args:
            token: OAuth token dict

        Returns:
            User info dict
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.twitter.com/2/users/me",
                headers={"Authorization": f"Bearer {token['access_token']}"},
                params={"user.fields": "profile_image_url,verified"},
            )
            response.raise_for_status()
            user_data = response.json()["data"]

            return {
                "provider": "twitter",
                "provider_user_id": user_data["id"],
                "email": None,  # Twitter OAuth 2.0 doesn't provide email
                "email_verified": False,
                "name": user_data.get("name"),
                "username": user_data.get("username"),
                "picture": user_data.get("profile_image_url"),
                "verified": user_data.get("verified", False),
            }
