from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from video_extractor import extract_videos_task, convert_pptx_with_unzip
import os

app = FastAPI()

# Allow CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allowed origins
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
    temp_path = f"/shared_tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Queue the extraction task
    task = extract_videos_task.delay(temp_path)

    return {"task_id": str(task.id), "status": "Task sent to Celery worker"}