FROM python:3.10

WORKDIR /opt/etl

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip \
    && pip install -r /opt/etl/requirements.txt

COPY . .