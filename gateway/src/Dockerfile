FROM python:3.10-slim

WORKDIR .
RUN pwd && ls

COPY ../requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 install --upgrade pip
RUN apt-get -y update; apt-get -y install curl

EXPOSE 8000

COPY /src/main.py main.py

CMD ["python", "-m", "uvicorn", "--host", "0.0.0.0", "main:app"]