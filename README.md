# SlideSpeak coding challenge: Build a PowerPoint Video Extractor Tool

## The challenge!

Build a front-end implementation as well as a back-end service to extract videos from PowerPoint documents. This
should be done by implementing a simple **Next.js** front-end that posts a file to a **Python** server.
The front-end is also already implemented in the /frontend folder. You only need to add the
necessary logic to switch between the steps and convert the file via the API that you're going to build.

- The tool will be on a webpage similar to: [https://slidespeak.co/free-tools/convert-powerpoint-to-pdf/](https://slidespeak.co/free-tools/convert-powerpoint-to-pdf/)
- Figma Design: [https://www.figma.com/design/CRfT0MVMqIV8rAK6HgSnKA/SlideSpeak-Coding-Challenge?node-id=798-61](https://www.figma.com/design/CRfT0MVMqIV8rAK6HgSnKA/SlideSpeak-Coding-Challenge?node-id=798-61)

## Acceptance criteria

### Back-end API

- Should be implemented in Python.
- Extracting Videos from PowerPoint using a zip utility. This should support multiple processes in parallel. Preferably with a queue.
- The API should consist of one endpoint (POST /extract), which should do the following:
    1. Extracts the videos from the PowerPoint
    2. Uploads the videos to Amazon S3
       via [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
    3. Creates a presigned URL for the user to download

       [https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html)

       [https://medium.com/@aidan.hallett/securing-aws-s3-uploads-using-presigned-urls-aa821c13ae8d](https://medium.com/@aidan.hallett/securing-aws-s3-uploads-using-presigned-urls-aa821c13ae8d)

    4. Returns the presigned S3 url/urls to the client which allows the user to download the file (by opening the url in new
       tab)

### Front-end app

- The front-end should in terms of UX work similarly
  to [https://app.slidespeak.co/powerpoint-optimizer](https://app.slidespeak.co/powerpoint-optimizer)

## Nice to haves / tips

- Uses a queuing system like Celery and Redis
- The logic of the front-end ideally should not rely on useEffect too much since it can be difficult to track what is
  happening
- Tests
- Use conventional commit message style: https://www.conventionalcommits.org/en/v1.0.0/
- Lint your code
- Keep commits clean
- Setup with Docker Compose
