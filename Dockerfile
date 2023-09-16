# syntax=docker/dockerfile:1
FROM python:latest

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY test.py ./
COPY grades.csv ./
COPY students.csv ./
COPY submissions.csv ./
COPY tests.csv ./

CMD [ "python", "./test.py"]
