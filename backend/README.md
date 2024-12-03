## Prerequisites

- Having Docker installed on your system.

## Running the docker containers

The project includes a `Makefile` to simplify common Docker Compose tasks. You can use the following commands to manage your development and production environments:

### Available Commands

| Command       | Description                                                                                 |
|---------------|---------------------------------------------------------------------------------------------|
| `make start`  | Starts the development environment using `docker-compose.yml`.                             |
| `make build`  | Builds the Docker images and starts the development environment.                           |
| `make detach` | Builds the Docker images, starts the development environment in detached mode (background). |
| `make down`   | Stops and removes all containers, networks, and volumes defined in `docker-compose.yml`.   |
| `make prod`   | Starts the production environment using `docker-compose.prod.yml`.                         |
| `make prod-down` | Stops and removes all containers, networks, and volumes defined in `docker-compose.prod.yml`. |

---

### How to Use

1. **Start Development Environment**:
   - Run the following command to start your development environment:
     ```bash
     make start
     ```
   - This command will spin up the containers as defined in `docker-compose.yml`.

2. **Build and Start Containers**:
   - If you’ve made changes to your Dockerfile or dependencies, rebuild the containers with:
     ```bash
     make build
     ```

3. **Run in Detached Mode**:
   - To run the containers in the background, use:
     ```bash
     make detach
     ```

4. **Shut Down the Environment**:
   - To stop and clean up all containers, networks, and volumes, run:
     ```bash
     make down
     ```

5. **Start Production Environment**:
   - Use this command to start the production environment defined in `docker-compose.prod.yml`:
     ```bash
     make prod
     ```

6. **Shut Down Production Environment**:
   - To stop and clean up the production containers, use:
     ```bash
     make prod-down
     ```

***

## Pulgamecanica walkthoguh


### How Videos Are Stored in PowerPoint Files?

	PowerPoint files with the .pptx extension are essentially ZIP archives that follow the Office Open XML standard. 

	They contain various directories and XML files for slides, images, audio, and video. Videos embedded in a PowerPoint are usually stored as media files within the ppt/media folder inside the ZIP archive.


***

### How SlideSpeak Extracts Videos from .pptx Files

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

### Celery

Celery is running on a docker container.
You can use celery by implementing the decorator on the function you wish to queue.
Then you should use `.delay` to trigger the celery queue which will return the task id.
After that you can query the celery worker for the result, if any.

### Coding

Now we know what the python script should look like.

Fast API route:
**POST** _/extract_

- @params:
	- file: file.pptx

##### NOTE:
	How to make a test with postman when a post requires a named file parameter?
	You should go to postman and change the request to a post.
	Then on the Body section choose form-data.
	Then hover on the `Key` section and choose "File" on the dropdown.
	Then you can put the key `file` and choose the file for the value.

### Structure

We will use fastapi to create an endpoint where we can `post` pptx files and get a response appropiate for the desired output. (likely to be a ref. to the S3 bucket were we will store the videos)

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py  # Entry point for FastAPI app
│   ├── tasks.py # Logic for video extraction and S3 upload
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
└── .env
```

### Dependencies

- fastapi: Framework for building the backend API.
- uvicorn: ASGI server for running the FastAPI application.
- boto3: AWS SDK for Python to interact with Amazon S3.
- python-multipart: Required by FastAPI to handle file uploads.
- celery: Task queue system for parallel processing.
- redis: Backend for Celery and message broker.
- aiofiles: Asynchronous file I/O for FastAPI when saving uploaded files


### CORS

This is the current CORS setup:

```py
# main.py

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allowed HTTP methods
    allow_headers=["*"],  # Allowed headers
)
```

If you want to run in production or test it in your local network, you will need to change the configuration accordingly