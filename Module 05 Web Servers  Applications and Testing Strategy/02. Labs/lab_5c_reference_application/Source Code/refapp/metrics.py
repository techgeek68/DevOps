from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

REQUESTS = Counter(
    "refapp_http_requests_total", "HTTP requests", ["method", "endpoint", "status"]
)
ORDERS_CREATED = Counter(
    "refapp_orders_created_total", "Orders written to the database"
)

def render_metrics() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST
