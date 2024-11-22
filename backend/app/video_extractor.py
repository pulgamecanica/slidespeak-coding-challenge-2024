import os
import subprocess
from celery import Celery
import boto3
from botocore.exceptions import NoCredentialsError

# Setup Celery
celery = Celery(
    "tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
)

# S3 Configuration
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")

# AWS S3 Client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION,
)


def convert_pptx_with_unzip(pptx_file_path, output_dir):
    """
    Convert the .pptx file to a raw directory structure using Unzip.
    """
    os.makedirs(output_dir, exist_ok=True)
    unzip_command = [
        "unzip",
        "-j",
        pptx_file_path,
        "ppt/media/*",
        "-d",
        output_dir,
    ]

    try:
        subprocess.run(unzip_command, check=True, shell=False)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Unzip conversion failed: {e}")
    if not os.path.exists(output_dir):
        raise RuntimeError(f"Unzip didnt provide the output file: {output_dir}")



def extract_videos_from_directory(input_dir):
    """
    Extract video files from the converted directory.
    """
    video_extensions = {".mp4", ".mov", ".avi", ".mkv"}
    videos = []

    # Look for media files in the `ppt/media/` directory
    if not os.path.exists(input_dir):
        raise RuntimeError(f"Unusual pptx format, no {input_dir} founded")

    for file in os.listdir(input_dir):
        if os.path.splitext(file)[1].lower() in video_extensions:
            videos.append(os.path.join(input_dir, file))

    return videos


def upload_to_s3(file_path, s3_key):
    """
    Upload a file to S3 and generate a presigned URL.
    """
    try:
        s3_client.upload_file(file_path, S3_BUCKET_NAME, s3_key)
        return s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET_NAME, "Key": s3_key},
            ExpiresIn=3600,  # URL expires in 1 hour
        )
    except NoCredentialsError:
        raise RuntimeError("AWS credentials not found.")
    except Exception as e:
        raise RuntimeError(f"Error uploading to S3: {e}")


# @celery.task
def extract_videos_task(file_path):
    """
    Celery task to extract videos from a PowerPoint file.
    """
    output_dir = f"{file_path.replace(' ', '')}_output"
    try:
        # Step 1: Convert the PowerPoint file to a ZIP-like structure using Unzip
        convert_pptx_with_unzip(file_path, output_dir)

        # Step 2: Extract videos from the converted directory
        extracted_videos = extract_videos_from_directory(output_dir)
        print("Extracted Videos", extracted_videos)

        if not extracted_videos:
            return {"message": "No videos found in the presentation.", "urls": []}

        # # Step 3: Upload videos to S3 and generate presigned URLs
        presigned_urls = []
        for video in extracted_videos:
            s3_key = f"videos/{os.path.basename(video)}"
            presigned_url = upload_to_s3(video, s3_key)
            presigned_urls.append(presigned_url)

        return {"message": "Videos extracted and uploaded successfully.", "urls": presigned_urls}

    finally:
        # Clean up temporary files and directories
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(output_dir):
            subprocess.run(["rm", "-rf", output_dir], check=False)
