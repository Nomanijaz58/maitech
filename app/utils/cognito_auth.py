"""
Cognito JWT Authentication utilities for FastAPI
"""
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
from app.core.cognito import verify_cognito_token

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Validate JWT token and return current user information
    
    Args:
        credentials: HTTP Bearer token from Authorization header
        
    Returns:
        Dict containing user information from JWT token
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # Extract token from credentials
        token = credentials.credentials
        
        # Verify and decode the token
        decoded_token = verify_cognito_token(token)
        
        # Extract user information from token
        user_info = {
            'sub': decoded_token.get('sub'),  # User ID
            'email': decoded_token.get('email'),
            'name': decoded_token.get('name'),
            'cognito:username': decoded_token.get('cognito:username'),
            'token_use': decoded_token.get('token_use'),
            'aud': decoded_token.get('aud'),
            'iss': decoded_token.get('iss'),
            'exp': decoded_token.get('exp'),
            'iat': decoded_token.get('iat'),
            'auth_time': decoded_token.get('auth_time')
        }
        
        return user_info
        
    except ValueError as e:
        # Token validation failed
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        # Unexpected error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
