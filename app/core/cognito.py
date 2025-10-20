from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError

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
        raise ValueError(e.response.get("Error", {}).get("Message", str(e)))


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
        raise ValueError(e.response.get("Error", {}).get("Message", str(e)))


