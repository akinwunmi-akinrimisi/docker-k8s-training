FROM python:3.10-slim-bullseye
ARG author
ENV AUTHOR=$author
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY src .
EXPOSE 9900
CMD [ "python3", "app.py"]
