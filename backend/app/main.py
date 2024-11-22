from fastapi import FastAPI, UploadFile, HTTPException, BackgroundTasks
from video_extractor import extract_videos_task, convert_pptx_with_unzip
import os

app = FastAPI()

@app.post("/extract")
async def extract_videos(file: UploadFile):
    # if file.content_type != "application/vnd.openxmlformats-officedocument.presentationml.presentation":
    if file.content_type != "application/vnd.openxmlformats-officedocument.presentationml.presentation":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PowerPoint file.")
    
    # Save file temporarily
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Queue the extraction task
    videos = extract_videos_task(temp_path)

    # Clean up temporary files and directories
    if os.path.exists(temp_path):
        os.remove(temp_path)
    return {"task": videos}
