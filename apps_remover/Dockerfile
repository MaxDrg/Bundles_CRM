FROM python:3.9.7-buster

WORKDIR /remover

COPY requirements.txt /remover

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .