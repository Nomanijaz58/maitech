from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from app.utils.cognito_auth import security, verify_cognito_token
from app.db.documents.user import User


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    Get the current authenticated user from the database using Beanie.
    
    This function validates the Cognito token and fetches the corresponding user
    from MongoDB using Beanie ODM. Use this dependency in all authenticated routes.
    
    Args:
        credentials: HTTP Bearer token from Authorization header
        
    Returns:
        User: The authenticated user document from MongoDB
        
    Raises:
        HTTPException: If token is invalid or user is not found in database
    """
    try:
        # Verify Cognito token
        token = credentials.credentials
        decoded_token = verify_cognito_token(token)
        
        # Extract email from token
        email = decoded_token.get('email')
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email not found in token"
            )
        
        # Fetch user from database using Beanie
        user = await User.find_one(User.email == email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in database"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user: {str(e)}"
        )


# Keep verify_cognito_user for backward compatibility during migration
async def verify_cognito_user(current_user: User = Depends(get_current_user)):
    """
    Deprecated: Use get_current_user instead.
    Kept for backward compatibility during migration.
    """
    return {"user_id": str(current_user.id), "email": current_user.email}


