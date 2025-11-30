FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir paho-mqtt confluent-kafka

CMD ["python", "m_k.py"]