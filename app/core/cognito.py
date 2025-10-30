from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError
import jwt
import requests
from datetime import datetime

from app.core.config import configurations


def _get_cognito_client():
    # Use explicit Cognito region from configuration
    session_kwargs = {"region_name": configurations.COGNITO_REGION}
    if configurations.AWS_ACCESS_KEY_ID and configurations.AWS_SECRET_ACCESS_KEY:
        session_kwargs.update(
            {
                "aws_access_key_id": configurations.AWS_ACCESS_KEY_ID,
                "aws_secret_access_key": configurations.AWS_SECRET_ACCESS_KEY,
            }
        )
    return boto3.client("cognito-idp", **session_kwargs)


def get_cognito_public_keys():
    """Fetch Cognito public keys for JWT verification"""
    try:
        url = f"https://cognito-idp.{configurations.COGNITO_REGION}.amazonaws.com/{configurations.COGNITO_USER_POOL_ID}/.well-known/jwks.json"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise ValueError(f"Failed to fetch Cognito public keys: {str(e)}")


def verify_cognito_token(token: str) -> Dict[str, Any]:
    """Verify and decode a Cognito JWT token"""
    try:
        # Get the public keys
        keys = get_cognito_public_keys()
        
        # Decode the token header to get the key ID
        header = jwt.get_unverified_header(token)
        kid = header.get('kid')
        
        if not kid:
            raise ValueError("Token header missing 'kid'")
        
        # Find the matching public key
        public_key = None
        for key in keys['keys']:
            if key['kid'] == kid:
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
                break
        
        if not public_key:
            raise ValueError("No matching public key found")
        
        # Verify and decode the token
        decoded_token = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            audience=configurations.COGNITO_CLIENT_ID,
            issuer=f"https://cognito-idp.{configurations.COGNITO_REGION}.amazonaws.com/{configurations.COGNITO_USER_POOL_ID}"
        )
        
        # Check token expiration
        if 'exp' in decoded_token:
            exp_timestamp = decoded_token['exp']
            if datetime.utcnow().timestamp() > exp_timestamp:
                raise ValueError("Token has expired")
        
        return decoded_token
        
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid token: {str(e)}")
    except Exception as e:
        raise ValueError(f"Token verification failed: {str(e)}")


def sign_up(email: str, password: str, name: Optional[str] = None) -> Dict[str, Any]:
    client = _get_cognito_client()
    try:
        params: Dict[str, Any] = {
            "ClientId": configurations.COGNITO_CLIENT_ID,
            "Username": email,
            "Password": password,
            "UserAttributes": [{"Name": "email", "Value": email}],
        }
        if name:
            params["UserAttributes"].append({"Name": "name", "Value": name})
        response = client.sign_up(**params)
        return response
    except ClientError as e:
        error_message = e.response.get("Error", {}).get("Message", str(e))
        raise ValueError(f"Cognito sign_up failed: {error_message}")
    except Exception as e:
        raise ValueError(f"Unexpected error during sign_up: {str(e)}")


def confirm_sign_up(email: str, code: str) -> Dict[str, Any]:
    client = _get_cognito_client()
    try:
        response = client.confirm_sign_up(
            ClientId=configurations.COGNITO_CLIENT_ID,
            Username=email,
            ConfirmationCode=code,
        )
        return response
    except ClientError as e:
        error_message = e.response.get("Error", {}).get("Message", str(e))
        raise ValueError(f"Cognito confirm_sign_up failed: {error_message}")
    except Exception as e:
        raise ValueError(f"Unexpected error during confirm_sign_up: {str(e)}")


def login(email: str, password: str) -> Dict[str, Any]:
    client = _get_cognito_client()
    try:
        response = client.initiate_auth(
            ClientId=configurations.COGNITO_CLIENT_ID,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": email,
                "PASSWORD": password,
            },
        )
        return response
    except ClientError as e:
        error_message = e.response.get("Error", {}).get("Message", str(e))
        raise ValueError(f"Cognito login failed: {error_message}")
    except Exception as e:
        raise ValueError(f"Unexpected error during login: {str(e)}")


def reset_password(email: str) -> Dict[str, Any]:
    """Initiate forgot password flow in Cognito"""
    client = _get_cognito_client()
    try:
        response = client.forgot_password(
            ClientId=configurations.COGNITO_CLIENT_ID,
            Username=email,
        )
        return response
    except ClientError as e:
        error_message = e.response.get("Error", {}).get("Message", str(e))
        raise ValueError(f"Cognito forgot_password failed: {error_message}")
    except Exception as e:
        raise ValueError(f"Unexpected error during forgot_password: {str(e)}")


def confirm_forgot_password(email: str, confirmation_code: str, new_password: str) -> Dict[str, Any]:
    """Confirm forgot password with new password"""
    client = _get_cognito_client()
    try:
        response = client.confirm_forgot_password(
            ClientId=configurations.COGNITO_CLIENT_ID,
            Username=email,
            ConfirmationCode=confirmation_code,
            Password=new_password,
        )
        return response
    except ClientError as e:
        error_message = e.response.get("Error", {}).get("Message", str(e))
        raise ValueError(f"Cognito confirm_forgot_password failed: {error_message}")
    except Exception as e:
        raise ValueError(f"Unexpected error during confirm_forgot_password: {str(e)}")






