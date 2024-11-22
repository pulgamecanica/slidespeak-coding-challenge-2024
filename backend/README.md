## Prerequisites

- Having Docker installed on your system.

## Running the docker container

```bash
docker compose up --build
```

***

## Pulgamecanica walkthoguh


### Analysis

#### How Videos Are Stored in PowerPoint Files?

	PowerPoint files with the .pptx extension are essentially ZIP archives that follow the Office Open XML standard. 

	They contain various directories and XML files for slides, images, audio, and video. Videos embedded in a PowerPoint are usually stored as media files within the ppt/media folder inside the ZIP archive.


***

#### How SlideSpeak Extracts Videos from .pptx Files

    Treat .pptx as a ZIP Archive: Use unzip tool extract its contents.

```py
subprocess.run(
        ["unzip", "-j", pptx_file_path, "ppt/media/*", "-d", output_path],
        check=True,
        shell=False,
    )
```

As seen here: https://github.com/SlideSpeak/image-extractor-cli/blob/30c5ad96ffbc3aaea63b01928630b3efe87e62e9/image_extractor.py#L110C9-L114C10


	unzip: Unzips the file.
	-j: Junk the directory structure (extracts files without retaining folder hierarchy).
	pptx_file_path: Path to the .pptx file.
	ppt/media/*: Extracts only files from the ppt/media/ directory.
	-d output_path: Specifies the directory to extract the files.


    Any file with video formats such as .mp4, .mov, .avi, etc., is likely a video.

    Extract Relevant Files: Extract the video files into a temporary directory for further processing or upload.

***

### Coding

Now we know what the python script should look like.

Instead of using the unzip tool we will use unoserver which is more appropiate and also suggested implicitly by the docker-compose providede challenge file.

Fast API route:
**POST** _/extract_

- @params:
	- file: file.pptx

##### NOTE:
	I am happy :D !!!
	I learnt something new!
	How to make a test with postman when a post requires a named file parameter.
	You should go to postman and change the request to a post.
	Then on the Body section choose form-data.
	Then hover on the `Key` section and choose "File" on the dropdown.
	Then you can put the key `file` and choose the file for the value.

#### Structure

We will use fastapi to create an endpoint where we can `post` pptx files and get a response appropiate for the desired output. (likely to be a ref. to the S3 bucket were we will store the videos)

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py  # Entry point for FastAPI app
│   ├── tasks.py # Logic for video extraction and S3 upload
│   ├── celery_worker.py # Celery worker setup
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
└── .env
```

### Dependencies

- fastapi: Framework for building the backend API.
- uvicorn: ASGI server for running the FastAPI application.
- unoserver: A tool for handling pptx files thorugh a server
- boto3: AWS SDK for Python to interact with Amazon S3.
- python-multipart: Required by FastAPI to handle file uploads.
- celery: Task queue system for parallel processing.
- redis: Backend for Celery and message broker.
- aiofiles: Asynchronous file I/O for FastAPI when saving uploaded files
- watchgod: For file reloading