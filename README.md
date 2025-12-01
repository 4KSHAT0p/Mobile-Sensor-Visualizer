# Android Sensor Data Visualizer

This project demonstrates a complete real-time data pipeline for collecting Android sensor data and visualizing it using modern data engineering tools.

The system is built for high-frequency sensor ingestion, scalability, and real-time analytics.


<img width="1544" height="697" alt="image" src="https://github.com/user-attachments/assets/5e812c2d-25e3-40c5-aa13-2f0c85c9f10e" />



## Features

- Real-time device sensor monitoring (even GPS).

- High throughput data ingestion via **Kafka**

- Efficient time-series storage using **TimescaleDB**

- Custom elegant dashboards using **Grafana**

- Live updating stats & time-series charts

- Fully containerized deployment using **Docker**.

---

## Architecture

### 1. Android Sensor Client

An android app, [SensorSpot](https://github.com/UmerCodez/SensorSpot) reads various sensors' data (we can choose sensors from the app) and publishes it to a public MQTT broker.

Special thanks to [UmerCodez](https://github.com/UmerCodez).


### 2. MQTT broker

The broker (**EMQX**) receives messages from the mobile app on the topic:

`android/sensor`

It acts as the first layer of transport for lightweight sensor messages.

### 3. Kafka

**Apache Kafka** is an open-source distributed event streaming platform used for high-performance data pipelines, streaming analytics, data integration, and mission-critical applications.

A custom **Python** service is used to bridge MQTT messages into Kafka.
The script subscribes to all sensor topics on the MQTT broker, parses the incoming JSON payload, and publishes the same events into a Kafka topic (sensors).

### 4. TimescaleDB

**TimescaleDB** is a time-series database built on top of **PostgreSQL**. It is designed for fast ingestion and efficient querying of timestamped data, which makes it ideal for high-frequency Android sensor streams.

In this project, TimescaleDB stores all incoming sensor events from **Kafka** in a single hypertable.

### 5. Grafana

**Grafana** is used as the frontend dashboard for visualizing all the sensor data stored in database. Once the database receives continuous sensor values from Kafka, Grafana queries the hypertable and renders real-time charts, stats, and insights.

We can make our own custom visualizations using Grafana for better monitoring of the data.



<br><br>


### The entire system is deployed fully inside Docker containers.
 
No service runs locally on the host machine; every component is isolated, reproducible, and easily portable.




<br><br>

## How to run


### 1️. Open SensorSpot

Open the app and set the broker address and port number as `broker.emqx.io` and `1883` and connect to the broker.



### 2. Start all Docker services

Build and start every container (MQTT, Kafka, TimescaleDB, Grafana, Python services) using:

```
docker compose up -d --build
```


### 3. Enter the Reader container

```
docker exec -it <reader_name> bash
```


Inside this container, run  **m_k.py**.

Leave it running.


### 4. Enter the Producer container

```
docker exec -it <writer_name> bash
```


Inside this container, run  **k_d.py**.

Leave it running.


_We can get the names of the containers via_:

```
    docker ps 
```

### 4. Open Grafana and start visualizing

Open Grafana on localhost:3000 and enter `admin` as usename and password. Choose PostgreSQL as a data source and create a connection. 
```
Host: timescaledb:5432
Database: your_db_name
User: your_pg_user
Password: your_pg_pass
```

Now we can start making different real-time visualizations.


