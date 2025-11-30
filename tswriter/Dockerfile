FROM python:3.11-slim

WORKDIR /app

# Install python deps (no gcc needed now)
RUN pip install --no-cache-dir \
    psycopg2-binary \
    confluent-kafka

COPY k_d.py .

CMD ["python", "k_d.py"]
