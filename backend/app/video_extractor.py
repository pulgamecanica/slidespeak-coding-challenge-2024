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

    Args:
        pptx_file_path (str): Path to the pptx file.
        output_dir (str): Path to the output directory (*_output)
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


def filter_files_by_extension(output_dir, extensions):
    """
    Filters files in the given directory, keeping only those with specified extensions.

    Args:
        output_dir (str): Path to the directory to filter.
        extensions (set): A set of file extensions to keep (e.g., {".mp4", ".mov"}).
    """
    for file in os.listdir(output_dir):
        if not any(file.lower().endswith(ext) for ext in extensions):
            os.remove(os.path.join(output_dir, file))


def upload_to_s3(file_path, s3_key):
    """
    Upload a file to S3 and generate a presigned URL.

    Args:
        file_path (str): The file to be uploadedr.
        s3_key (set): The s3 key, where it will live in the bucket.
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

    Args:
        file_path (str): Path to the downloaded pptx file.
    """
    output_dir = f"{file_path.replace(' ', '')}_output"
    zip_path = f"{file_path.replace(' ', '')}.zip"

    try:
        # Make sure path does not exist, could exist if an error occured and didnt cleanup
        if os.path.exists(output_dir):
            subprocess.run(["rm", "-rf", output_dir], check=False)

        # Step 1: Convert the PowerPoint file to a ZIP-like structure using Unzip
        convert_pptx_with_unzip(file_path, output_dir)

        # Step 2: Extract videos from the converted directory
        video_extensions = {".mp4", ".mov", ".avi", ".mkv"}
        filter_files_by_extension(output_dir, video_extensions)
        extracted_files = os.listdir(output_dir)

        if not extracted_files:
            raise RuntimeError("No video files were found in the uploaded presentation.")

        if len(extracted_files) == 1:
            # Only one video file, upload it directly
            file_to_upload = os.path.join(output_dir, extracted_files[0])
            s3_key = f"videos/{os.path.basename(file_to_upload)}"
        else:
            # Multiple files, zip the directory
            shutil.make_archive(zip_path.replace(".zip", ""), "zip", output_dir)
            file_to_upload = zip_path
            s3_key = f"videos/{os.path.basename(zip_path)}"

        # Step 3: Upload videos to S3 and generate presigned URLs
        presigned_url = upload_to_s3(file_to_upload, s3_key)

        return {"message": "Videos extracted and uploaded successfully.", "url": presigned_url}

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
        if os.path.exists(zip_path):
            os.remove(zip_path)
