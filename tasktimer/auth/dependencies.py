from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from .config import settings
from .cognito import decode_and_validate_token
from .models import AuthenticatedUser

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> AuthenticatedUser:
    """
    FastAPI dependency that extracts and validates JWT from Authorization header.

    Returns mock user when AUTH_DISABLED=true for local development.
    Raises 401 for missing or invalid tokens when auth is enabled.
    """
    if settings.AUTH_DISABLED:
        return AuthenticatedUser(
            user_id="dev-user-001",
            email="dev@localhost",
        )

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        payload = decode_and_validate_token(token)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user info from token
    # 'sub' is the Cognito user ID (UUID format)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject claim",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email = payload.get("email")

    return AuthenticatedUser(user_id=user_id, email=email)
