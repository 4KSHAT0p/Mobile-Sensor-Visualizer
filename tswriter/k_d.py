import os
import json
import psycopg2
from confluent_kafka import Consumer

# -----------------------------------
# Environment variables from docker-compose
# -----------------------------------
KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "sensors"

PG_HOST = "timescaledb"
PG_DB = "sensors"
PG_USER = "postgres"
PG_PASS = "postgres"
# -----------------------------------
# Connect to TimescaleDB
# -----------------------------------
conn = psycopg2.connect(host=PG_HOST, dbname=PG_DB, user=PG_USER, password=PG_PASS)
conn.autocommit = True
cur = conn.cursor()

# -----------------------------------
# Create table + hypertable (safe if exists)
# -----------------------------------

# Create table
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS sensor_data (
        ts TIMESTAMPTZ NOT NULL,
        sensor_type TEXT NOT NULL,
        values JSONB NOT NULL
    );
    """
)

# Convert it into a hypertable
cur.execute(
    """
    SELECT create_hypertable(
        'sensor_data',
        'ts',
        if_not_exists => TRUE
    );
    """
)


print("✔ TimescaleDB ready")

# -----------------------------------
# Kafka Consumer
# -----------------------------------
consumer = Consumer(
    {
        "bootstrap.servers": KAFKA_BROKER,
        "group.id": "ts-writer-group",
        "auto.offset.reset": "earliest",
    }
)

consumer.subscribe([KAFKA_TOPIC])

print(f"✔ Listening to Kafka topic: {KAFKA_TOPIC}")

# -----------------------------------
# Main loop
# -----------------------------------
while True:
    msg = consumer.poll(1.0)

    if msg is None:
        continue
    if msg.error():
        print("Consumer error:", msg.error())
        continue

    try:
        payload = msg.value().decode()
        data = json.loads(payload)

        sensor_type = data["type"]
        values = data["values"]

        # Convert ns → seconds → proper timestamp
        ts_ns = int(data["timestamp"])
        ts = ts_ns / 1_000_000_000.0  # convert nanoseconds to seconds

        cur.execute(
            """
            INSERT INTO sensor_data (ts, sensor_type, values)
            VALUES (to_timestamp(%s), %s, %s)
            """,
            (ts, sensor_type, json.dumps(values)),
        )

        print(f"✔ Inserted sensor data of the type {sensor_type}")

    except Exception as e:
        print("❌ Error parsing/inserting:", e)
        print("Payload:", msg.value())
