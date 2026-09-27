from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from app.config import settings
from app.models.user import UserRole
from app.schemas.auth import TokenData


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Generates a signed JWT access token containing claims."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": now})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> TokenData | None:
    """Decodes and validates a JWT access token, returning TokenData if valid."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str: str = payload.get("sub")
        role_str: str = payload.get("role")

        if user_id_str is None or role_str is None:
            return None

        return TokenData(
            user_id=int(user_id_str),
            role=UserRole(role_str)
        )
    except (JWTError, ValueError):
        return None
