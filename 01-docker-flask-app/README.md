# Docker: Containerizing a Simple Flask App

This exercise has the following objectives:
- Understanding a simple python flask app
- Writing a simple Dockerfile
- Building docker images
- Running docker containers with built image
- Pushing docker images to a container registry

## Pre-requisites
- Docker should be installed. Details on installing can be found [here](https://docs.docker.com/get-docker/)

## Understanding a simple python flask app
[Flask](https://flask.palletsprojects.com/en/2.2.x/) is a Python framework used in developing web apps.

The app we have here (under the src/ folder) does the following:
- runs on port 9900
- when the / path is accessed on the webapp, the default template (templates/default.html) is rendered
- when the /author path is accessed on the webapp, the value of the AUTHOR environment variable (if set) is returned

### Usage
Note that the necessary python dependencies are available in the requirements.txt. These can be installed by running the command "pip install -r requirements.txt"

- To run the app locally, `python ${PATH_TO_REPO}/01-docker-flask-app/src/app.py`

## Writing a simple Dockerfile
### Background
- A container is a unit of software that packages code and its dependencies so the application runs quickly and reliably across computing environments.
- A Dockerfile is a text document that contains all the commands a user could call on the command line to assemble a container image.
- [This](https://docs.docker.com/engine/reference/builder/) is the official Dockerfile reference that covers all the different commands that can be used.

### Writing a Dockerfile for our Flask application
The Dockerfile in 01-docker-flask-app/Dockerfile builds a simple container image for the application.
The following explains what each line in the Dockerfile achieves

#### Line 1: 
`FROM python:3.9-slim-buster`

Container images are built in layers so the first line of a Dockerfile is normally to invoke an appropriate base image. These can be found on public Docker registries like [Dockerhub](https://hub.docker.com/).
Given that this is a python3 application. We will use a python3 image. The [3.9-slim-buster image](https://hub.docker.com/layers/library/python/3.9-slim-buster/images/sha256-027813131fa3e8625620e561a865659a7fc251ed47da4de1696def371199f80a?context=explore) to be specific.
Note that ideally you want the smallest base image you can use thus why we opted for the slim-buster version here.

#### Lines 2-3: 
```
ARG author
ENV AUTHOR=$author
```

These lines set up a [build argument](https://blog.programster.org/docker-build-arguments) called `author` and sets the environment variable `AUTHOR` to the value of this argument.
This allows us to set the value of the environment variable whilst building our container image. [This blog](https://vsupalov.com/docker-build-pass-environment-variables/) goes into some more detail.
Remember this is important as our application returns the value of the `AUTHOR` environment variable when the `/author` path is accessed.

#### Line 4: 
`WORKDIR /app`

This command creates a new working directory for us to put all our app-related files and start the application.
Note the WORKDIR syntax is `WORKDIR /path/to/workdir`


#### Lines 5-6: 
```
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
```

These commands are to set up our dependencies. We copy the [requirements file] (https://realpython.com/lessons/using-requirement-files/#:~:text=A%20requirements%20file%20is%20a,current%20projects%20dependencies%20to%20stdout%20) which contains all the project dependencies.
Thereafter, we run the pip install command to install said dependencies
Note the COPY syntax is `COPY <source> <destination>`
Note the RUN syntax is `RUN <command>`


#### Line 7: 
`COPY src .`

This command copies the contents of our 01-docker-flask-app/src folder to the container working directory

#### Line 8: 
`EXPOSE 9900`

This command exposes the 9900 port which our application runs on.
Note the EXPOSE syntax is `EXPOSE <port number>`

#### Line 9: 
`CMD [ "python3", "app.py"]`

This command starts our application within the container.
Note the CMD syntax used is `CMD ["executable","param1","param2",...]`

### Building docker images
To build the Docker image for our flask app:
- Go to the directory of the Dockerfile: `cd ${PATH_TO_REPO}/01-docker-flask-app`
- Build the image with an appropriate tag and author value i.e.`docker build -t <image tag> . --build-arg author=<author value>`. For example: `docker build -t testapp:latest . --build-arg author=Cloudboosta`

### Running docker container with built image
To run a container with the image built in the previous step,
- Run the container with the 9900 port exposed: `docker run -p 9900:9900 testapp:latest`

### Pushing docker images to a container registry
It is good practice to push built container images to a registry. This means they can be reused and exist outside local machines.
Building and pushing of container images is typically done within a CI/CD pipeline. 
There are numerous registries that can be used such as Dockerhub, Github Container Registry, Amazon ECR and so on.
We can use GHCR and instructions on pushing images to GHCR can be found [here](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry) with a TLDR version [here](https://nikiforovall.github.io/docker/2020/09/19/publish-package-to-ghcr.html).
