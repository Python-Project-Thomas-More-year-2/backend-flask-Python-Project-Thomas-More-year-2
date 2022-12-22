FROM python:3.8.3-slim

WORKDIR /app

RUN apt-get update \
    && apt-get -y install libpq-dev gcc

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "app.py", "--host=0.0.0.0"]
