import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import PyJWKClient

from app.core.config import settings
from app.db.documents.user import User

COGNITO_REGION = settings.COGNITO_REGION
COGNITO_USER_POOL_ID = settings.COGNITO_USER_POOL_ID
COGNITO_CLIENT_ID = settings.COGNITO_CLIENT_ID
JWKS_URL = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json"

security = HTTPBearer()
jwk_client = PyJWKClient(JWKS_URL)


def verify_token(token: str) -> dict:
    """Verify the token using Cognito JWKS"""
    signing_key = jwk_client.get_signing_key_from_jwt(token).key
    return jwt.decode(
        token,
        signing_key,
        algorithms=["RS256"],
        audience=COGNITO_CLIENT_ID,
        issuer=f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}",
    )


async def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)) -> User:
    try:
        verified_token = verify_token(token.credentials)
        email = verified_token.get("email")
        user = await User.find_one(User.email == email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
