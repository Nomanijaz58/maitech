# MaiTech Backend Setup Guide

This is a FastAPI backend application with MongoDB, AWS Cognito authentication, and SendGrid email service.

## Prerequisites

- Python 3.9+ installed
- MongoDB connection string
- AWS Cognito credentials
- SendGrid API key

## Setup Instructions

### 1. Create and Activate Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create Environment Variables File

Create a `.env` file in the project root with the following variables:

```env
# Application Settings
APP_NAME=MaiTech
FRONTEND_URL=http://localhost:3000

# MongoDB Configuration
MONGODB_URL=your_mongodb_connection_string

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Email Configuration (SendGrid)
MAIL_FROM=your-email@example.com
SENDGRID_API_KEY=your_sendgrid_api_key

# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key

# AWS Cognito Configuration (Required)
COGNITO_REGION=us-east-1
COGNITO_USER_POOL_ID=your_cognito_user_pool_id
COGNITO_CLIENT_ID=your_cognito_client_id
```

**Note:** Replace all placeholder values with your actual credentials.

### 4. Run the Application

#### Option 1: Using uvicorn directly (Development)
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Option 2: Using Python directly
```bash
python main.py
```

### 5. Access the Application

Once running, you can access:

- **API Documentation (Swagger UI):** http://localhost:8000/api/docs
- **ReDoc Documentation:** http://localhost:8000/api/redoc
- **Health Check:** http://localhost:8000/api/health
- **Root Endpoint:** http://localhost:8000/

## Required Environment Variables

The following environment variables are **required** (will throw error if missing):

- `MONGODB_URL` - MongoDB connection string
- `COGNITO_REGION` - AWS Cognito region
- `COGNITO_USER_POOL_ID` - AWS Cognito User Pool ID
- `COGNITO_CLIENT_ID` - AWS Cognito Client ID
- `CORS_ALLOWED_ORIGINS` - Comma-separated list of allowed origins

## VS Code / Visual Studio Code Setup

### Recommended Extensions:
- Python extension by Microsoft
- Python Docstring Generator
- REST Client (for testing APIs)

### Launch Configuration (Optional)

Create `.vscode/launch.json` for debugging:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/main.py",
            "console": "integratedTerminal",
            "justMyCode": true,
            "envFile": "${workspaceFolder}/.env"
        }
    ]
}
```

## Common Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server with auto-reload (development)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run server (production-like)
uvicorn main:app --host 0.0.0.0 --port 8000

# Check installed packages
pip list

# Deactivate virtual environment
deactivate
```

## Project Structure

```
maitech_backend/
├── app/
│   ├── api/routes/     # API route handlers
│   ├── core/           # Core configuration and Cognito
│   ├── db/             # Database setup and models
│   ├── models/         # Data models
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic services
│   └── utils/          # Utility functions
├── main.py             # Application entry point
└── requirements.txt    # Python dependencies
```

## Troubleshooting

- **Import errors:** Ensure virtual environment is activated
- **Missing environment variables:** Check `.env` file exists and all required variables are set
- **MongoDB connection errors:** Verify `MONGODB_URL` is correct and MongoDB is accessible
- **Cognito errors:** Verify AWS credentials and Cognito configuration

