FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV BROKER_HOST=192.168.50.1
ENV BROKER_PORT=1883
ENV BROKER_USERNAME=pi_user
ENV BROKER_PASSWORD=group-1

ENTRYPOINT ["python", "main.py"]
