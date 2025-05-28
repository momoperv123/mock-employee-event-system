# Kafka Employee Event System

This project simulates an event-driven architecture using Kafka for handling employee data updates, built in Python with Docker.

## Key Concepts

- Producers: Simulate employee update events.
- Consumers: Departments like HR, Payroll, Compliance, etc., subscribe to updates and act accordingly.
- DLQ (Dead Letter Queue): Failed events are routed here with failure metadata.
- DLQ Monitor: Persists failed events to disk for observability.
- DLQ Replayer: Deduplicates and retries failed events from disk.

## Run the System

- docker-compose up --build

## Features
- Persistent storage via mounted Docker volumes (/data/)
- Retry logic for flaky consumers
- DLQ ingestion with detailed failure logs
- Replay mechanism with deduplication using hashed events

## Requirements
- Docker + Docker Compose
- Python 3.8+
- Kafka (runs in container)
