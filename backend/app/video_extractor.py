import os
import subprocess
import boto3
from celery import Celery
from botocore.exceptions import NoCredentialsError
from config import (
    AWS_ACCESS_KEY, AWS_SECRET_KEY, S3_BUCKET_NAME, AWS_REGION,
    CELERY_BROKER_URL, CELERY_BACKEND_URL,
    SOFT_TIME_LIMIT, TIME_LIMIT, MAX_CONVERT_TRIES
)
import shutil

# Setup Celery
celery = Celery(
    "video_extractor",
    broker=CELERY_BROKER_URL,
    backend=CELERY_BACKEND_URL,

)

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
    finally:
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

    if not videos:
        raise RuntimeError("No video files found in the extracted directory.")

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


@celery.task(
    soft_time_limit=SOFT_TIME_LIMIT,
    time_limit=TIME_LIMIT,
    max_retries=MAX_CONVERT_TRIES,
    priority=10,
)
def extract_videos_task(file_path):
    """
    Celery task to extract videos from a PowerPoint file.
    """
    output_dir = f"{file_path.replace(' ', '')}_output"

    try:
        # Make sure path does not exist, could exist if an error occured and didnt cleanup
        if os.path.exists(output_dir):
            subprocess.run(["rm", "-rf", output_dir], check=False)

        # Step 1: Convert the PowerPoint file to a ZIP-like structure using Unzip
        convert_pptx_with_unzip(file_path, output_dir)

        # Step 2: Extract videos from the converted directory
        extracted_videos = extract_videos_from_directory(output_dir)

        if not extracted_videos:
            return {"message": "No videos found in the presentation.", "urls": []}

        # # Step 3: Upload videos to S3 and generate presigned URLs
        presigned_urls = []
        for video in extracted_videos:
            s3_key = f"videos/{os.path.basename(video)}"
            presigned_url = upload_to_s3(video, s3_key)
            presigned_urls.append(presigned_url)

        return {"message": "Videos extracted and uploaded successfully.", "urls": presigned_urls}

    except RuntimeError as e:
        # Return a descriptive error message if a known error occurs
        return {"error": str(e)}

    except Exception as e:
        # Catch unexpected errors
        return {"error": f"An unexpected error occurred: {str(e)}"}

    finally:
        # Cleanup temporary files
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        if os.path.exists(file_path):
            os.remove(file_path)
