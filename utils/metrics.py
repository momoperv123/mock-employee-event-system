from prometheus_client import Counter, start_http_server

def init_metrics(port: int, consumer_name: str):
    start_http_server(port)

    processed = Counter("processed_events_total", "Total successfully processed events", ["consumer"])
    failures = Counter("processing_failures_total", "Total processing failures", ["consumer"])
    dlq = Counter("dlq_events_total", "Events sent to DLQ", ["consumer"])
    
    return {
        "processed": processed.labels(consumer=consumer_name),
        "failures": failures.labels(consumer=consumer_name),
        "dlq": dlq.labels(consumer=consumer_name),
    }