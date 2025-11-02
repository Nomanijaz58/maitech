from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from app.db.documents.user import User
from app.core.config import configurations
import boto3

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> User:
    """
    Extracts and verifies the currently authenticated user from Cognito token.
    Returns a user object for authorization checks.
    """
    if not token:
        # For development: create or return a default user
        # In production, this should raise HTTPException
        default_user = await User.find_one(User.email == "default@example.com")
        if not default_user:
            # Create a default user if it doesn't exist
            default_user = User(
                email="default@example.com",
                full_name="Default User"
            )
            await default_user.insert()
        return default_user
    
    try:
        # Use COGNITO_REGION if AWS_REGION is not set
        region = configurations.AWS_REGION or configurations.COGNITO_REGION
        client = boto3.client("cognito-idp", region_name=region)
        response = client.get_user(AccessToken=token)
        email = next(
            (attr["Value"] for attr in response["UserAttributes"] if attr["Name"] == "email"), None
        )
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token: email not found")

        user = await User.find_one(User.email == email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )

