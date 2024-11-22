from fastapi import FastAPI, UploadFile, HTTPException, BackgroundTasks
from video_extractor import extract_videos_task

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
    # task_id = extract_videos_task.delay(temp_path)
    task_id = extract_videos_task(temp_path)
    return {"task_id": task_id}
