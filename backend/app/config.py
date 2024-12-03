import os

# S3 Configuration
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")

# Celery Configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_BACKEND_URL = os.getenv("CELERY_BACKEND_URL", "redis://redis:6379/0")

# Local Directories
LOCAL_DOCUMENTS_DIR = "shared_tmp"

# Task Settings
MAX_CONVERT_TRIES = 5
SOFT_TIME_LIMIT = 120
TIME_LIMIT = 300

# CORS Settings
ALLOWED_ORIGINS = [
    "https://slidespeak.co",
    "http://localhost:3000",
]
