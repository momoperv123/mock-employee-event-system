# Kafka Employee Event System

This project simulates an event-driven architecture using Kafka for handling employee data updates, built in Python with Docker.

## Key Concepts

- Producers: Simulate employee update events.
- Consumers: Departments like HR, Payroll, Compliance, etc., subscribe to updates and act accordingly.
- DLQ (Dead Letter Queue): Failed events are routed here with failure metadata.
- DLQ Monitor: Persists failed events to disk for observability.
- DLQ Replayer: Deduplicates and retries failed events from disk.

## Features
- Persistent storage via mounted Docker volumes (/data/)
- Retry logic for flaky consumers
- DLQ ingestion with detailed failure logs
- Replay mechanism with deduplication using hashed events
- Observability with FastAPI, Prometheus, and Grafana
- Metrics endpoint (`/metrics`) for API instrumentation
- Pre-configured Grafana dashboard via Docker

## API Endpoints
- GET /health — Health check
- GET /payroll — Current payroll state
- GET /audit — Audit log
- GET /dlq — Failed events (latest)
- GET /dlq_replayed — Replayed DLQ events
- GET /metrics — Prometheus metrics

## Observability Dashboard
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
  - Login: admin / `admin
  - Add Prometheus as a data source (http://prometheus:9090)

## Requirements
- Docker + Docker Compose
- Python 3.8+
- Kafka (runs in container)
