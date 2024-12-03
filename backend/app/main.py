from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from video_extractor import extract_videos_task, celery
from config import ALLOWED_ORIGINS, LOCAL_DOCUMENTS_DIR
from celery.result import AsyncResult
import os
import uuid

app = FastAPI()

# Allow CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allowed HTTP methods
    allow_headers=["*"],  # Allowed headers
)

@app.post("/extract")
async def extract_videos(file: UploadFile):
    # if file.content_type != "application/vnd.openxmlformats-officedocument.presentationml.presentation":
    if file.content_type != "application/vnd.openxmlformats-officedocument.presentationml.presentation":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PowerPoint file.")
    
    # Save file temporarily
    temp_path = f"/{LOCAL_DOCUMENTS_DIR}/{uuid.uuid4()}_{file.filename}"
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Queue the extraction task
    task = extract_videos_task.delay(temp_path)

    return {"task_id": str(task.id), "status": "Task sent to Celery worker"}

@app.get("/get-result/{task_id}")
async def get_result(task_id: str):
    # Retrieve result from celery
    task = AsyncResult(task_id, app=celery)

    if task.ready():
        task_result = task.result
        task.forget()
        return {"status": "SUCCESS", "result": task_result}
    else:
        return {"status": "PENDING", "result": None}

