from fastapi import Depends, HTTPException


def verify_cognito_user():
    # TODO: Add AWS Cognito token validation
    return {"user_id": "example-student-123"}


