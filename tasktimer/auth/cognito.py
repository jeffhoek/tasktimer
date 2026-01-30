import time
from typing import Any

import requests
from cachetools import TTLCache
from jose import jwt, JWTError

from .config import settings

# Cache JWKS keys for 1 hour
_jwks_cache: TTLCache[str, dict[str, Any]] = TTLCache(maxsize=1, ttl=3600)
_JWKS_CACHE_KEY = "jwks"


def get_jwks() -> dict[str, Any]:
    """Fetch JWKS from Cognito, with 1-hour TTL caching."""
    if _JWKS_CACHE_KEY in _jwks_cache:
        return _jwks_cache[_JWKS_CACHE_KEY]

    response = requests.get(settings.jwks_url, timeout=10)
    response.raise_for_status()
    jwks = response.json()
    _jwks_cache[_JWKS_CACHE_KEY] = jwks
    return jwks


def get_signing_key(token: str) -> dict[str, Any]:
    """Get the signing key for the given token from JWKS."""
    jwks = get_jwks()
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")

    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key

    raise JWTError("Unable to find matching key in JWKS")


def decode_and_validate_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT token from Cognito.

    Validates:
    - Signature using JWKS
    - Expiry (exp claim)
    - Issuer (iss claim)
    - Audience (client_id in token_use=access or aud in token_use=id)
    """
    signing_key = get_signing_key(token)

    try:
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            issuer=settings.issuer,
            audience=settings.COGNITO_APP_CLIENT_ID,
            options={
                "verify_aud": True,
                "verify_iss": True,
                "verify_exp": True,
            },
        )
    except JWTError:
        # For access tokens, audience is in 'client_id' claim, not 'aud'
        # Try again without audience verification, then manually check
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            issuer=settings.issuer,
            options={
                "verify_aud": False,
                "verify_iss": True,
                "verify_exp": True,
            },
        )
        # Verify client_id for access tokens
        if payload.get("client_id") != settings.COGNITO_APP_CLIENT_ID:
            raise JWTError("Invalid audience/client_id")

    return payload


def clear_jwks_cache() -> None:
    """Clear the JWKS cache. Useful for testing."""
    _jwks_cache.clear()
