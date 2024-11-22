FROM python:3.9-slim

WORKDIR /backend

# Install system dependencies (unzip)
RUN apt-get update && apt-get install -y unzip

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY ./app /backend/app

# Run the FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
