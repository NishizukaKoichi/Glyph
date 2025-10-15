"""WebAuthn/Passkey authentication service."""

import secrets
from typing import Any

from webauthn import (
    generate_authentication_options,
    generate_registration_options,
    verify_authentication_response,
    verify_registration_response,
)
from webauthn.helpers import base64url_to_bytes, bytes_to_base64url
from webauthn.helpers.structs import (
    AuthenticationCredential,
    AuthenticatorSelectionCriteria,
    PublicKeyCredentialDescriptor,
    RegistrationCredential,
    UserVerificationRequirement,
)

from app.core.config import settings


class WebAuthnService:
    """Service for WebAuthn/Passkey operations."""

    def __init__(self):
        """Initialize WebAuthn service."""
        self.rp_id = settings.webauthn_rp_id
        self.rp_name = settings.webauthn_rp_name
        self.origin = settings.webauthn_origin

    def generate_registration_options(
        self, user_id: str, username: str, display_name: str
    ) -> dict[str, Any]:
        """Generate options for WebAuthn registration.

        Args:
            user_id: User ID
            username: Username
            display_name: Display name

        Returns:
            Registration options dict
        """
        options = generate_registration_options(
            rp_id=self.rp_id,
            rp_name=self.rp_name,
            user_id=user_id.encode(),
            user_name=username,
            user_display_name=display_name,
            authenticator_selection=AuthenticatorSelectionCriteria(
                user_verification=UserVerificationRequirement.PREFERRED,
            ),
        )

        return {
            "challenge": bytes_to_base64url(options.challenge),
            "rp": {"id": options.rp.id, "name": options.rp.name},
            "user": {
                "id": bytes_to_base64url(options.user.id),
                "name": options.user.name,
                "displayName": options.user.display_name,
            },
            "pubKeyCredParams": [
                {"type": param.type, "alg": param.alg}
                for param in options.pub_key_cred_params
            ],
            "timeout": options.timeout,
            "authenticatorSelection": {
                "userVerification": options.authenticator_selection.user_verification.value,
            },
            "attestation": options.attestation,
        }

    def verify_registration_response(
        self, credential: dict[str, Any], expected_challenge: str
    ) -> dict[str, Any]:
        """Verify WebAuthn registration response.

        Args:
            credential: Registration credential from client
            expected_challenge: Expected challenge

        Returns:
            Verification result with credential data
        """
        registration_credential = RegistrationCredential.model_validate(credential)

        verification = verify_registration_response(
            credential=registration_credential,
            expected_challenge=base64url_to_bytes(expected_challenge),
            expected_origin=self.origin,
            expected_rp_id=self.rp_id,
        )

        return {
            "verified": verification.credential_id is not None,
            "credential_id": bytes_to_base64url(verification.credential_id),
            "credential_public_key": bytes_to_base64url(
                verification.credential_public_key
            ),
            "sign_count": verification.sign_count,
            "aaguid": bytes_to_base64url(verification.aaguid),
            "credential_device_type": verification.credential_device_type,
            "credential_backed_up": verification.credential_backed_up,
        }

    def generate_authentication_options(
        self, credentials: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Generate options for WebAuthn authentication.

        Args:
            credentials: List of user's credentials

        Returns:
            Authentication options dict
        """
        allow_credentials = [
            PublicKeyCredentialDescriptor(id=base64url_to_bytes(cred["credential_id"]))
            for cred in credentials
        ]

        options = generate_authentication_options(
            rp_id=self.rp_id,
            allow_credentials=allow_credentials,
            user_verification=UserVerificationRequirement.PREFERRED,
        )

        return {
            "challenge": bytes_to_base64url(options.challenge),
            "timeout": options.timeout,
            "rpId": options.rp_id,
            "allowCredentials": [
                {
                    "type": cred.type,
                    "id": bytes_to_base64url(cred.id),
                    "transports": cred.transports,
                }
                for cred in options.allow_credentials
            ],
            "userVerification": options.user_verification.value,
        }

    def verify_authentication_response(
        self,
        credential: dict[str, Any],
        expected_challenge: str,
        credential_public_key: str,
        credential_current_sign_count: int,
    ) -> dict[str, Any]:
        """Verify WebAuthn authentication response.

        Args:
            credential: Authentication credential from client
            expected_challenge: Expected challenge
            credential_public_key: Stored public key
            credential_current_sign_count: Current sign count

        Returns:
            Verification result
        """
        authentication_credential = AuthenticationCredential.model_validate(credential)

        verification = verify_authentication_response(
            credential=authentication_credential,
            expected_challenge=base64url_to_bytes(expected_challenge),
            expected_origin=self.origin,
            expected_rp_id=self.rp_id,
            credential_public_key=base64url_to_bytes(credential_public_key),
            credential_current_sign_count=credential_current_sign_count,
        )

        return {
            "verified": verification.new_sign_count >= 0,
            "new_sign_count": verification.new_sign_count,
        }

    @staticmethod
    def generate_challenge() -> str:
        """Generate a random challenge for WebAuthn.

        Returns:
            Base64url-encoded challenge
        """
        return bytes_to_base64url(secrets.token_bytes(32))
