FROM python:3.9.7-buster

WORKDIR /checker

COPY requirements.txt /checker

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "checker.py"]