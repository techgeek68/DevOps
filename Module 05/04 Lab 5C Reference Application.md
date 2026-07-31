# Lab 5C. The Reference Application

This is the service the rest of the program keeps coming back to. It is small on purpose. It answers a health check, publishes metrics, and does one real piece of work behind a feature endpoint. Nothing about how it runs is baked into the code: the database it talks to, the port it listens on, the name it reports, all of that arrives from the environment. And there is not a single password written anywhere in the source.

You will run a real PostgreSQL in a container, wire the service to it, and watch an order get computed, stored, and read back.

The stack is Python 3.12 with Flask and Gunicorn, SQLAlchemy 2 for the database, the `psycopg2` driver, and `prometheus_client` for the metrics.

## 1. Lay out the project

```bash
mkdir -p ~/refapp/{refapp,tests} && cd ~/refapp
```

By the end of this lab the tree looks like this. The `tests/` and `migrations/` folders fill up in Labs 5D and 5E.

```
refapp/
├── refapp/
│   ├── __init__.py
│   ├── config.py       # everything configurable, read from the environment
│   ├── db.py           # engine and session, built from DATABASE_URL
│   ├── models.py       # the Order row
│   ├── pricing.py      # the pure math, no database in sight
│   ├── metrics.py      # the counters
│   └── app.py          # the Flask app: health, metrics, total, orders
├── requirements.txt    # exact versions, so a build is repeatable
├── .env.example        # the variables you must set, with fake values
└── .gitignore
```

## 2. Pin the dependencies

`requirements.txt`:

```
Flask==3.0.3
gunicorn==22.0.0
SQLAlchemy==2.0.31
psycopg2-binary==2.9.9
prometheus-client==0.20.0
```

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Start a real database in a container

The password comes in on the command line, from a variable, not from a file in the repo. Pin the image to a specific major version so this behaves the same next month:

```bash
export PGPASSWORD='ChangeMe_Local_Only'      # a local secret, and it stays out of git

docker run -d --name refapp-db \
    -e POSTGRES_USER=refapp \
    -e POSTGRES_PASSWORD="$PGPASSWORD" \
    -e POSTGRES_DB=refapp \
    -p 5432:5432 \
    docker.io/library/postgres:16

docker ps --filter name=refapp-db
```

If you are on RHEL and prefer Podman, `sudo dnf install -y podman podman-docker` gives you a `docker` command that runs these lines unchanged.

## 4. Read configuration from the environment

`refapp/config.py`. The database URL carries the credentials, so it is required with no fallback. If it is missing the app refuses to start, which is far better than starting against the wrong database:

```python
import os

class Config:
    def __init__(self) -> None:
        # Required. No default, no credentials in the code. Stop now if it is absent.
        try:
            self.database_url = os.environ["DATABASE_URL"]
        except KeyError as exc:
            raise RuntimeError(
                "DATABASE_URL is not set. Configuration comes from the environment; "
                "credentials never live in the source."
            ) from exc

        # These are not secret, so a sensible default is fine
        self.app_name = os.environ.get("APP_NAME", "refapp")
        self.port     = int(os.environ.get("PORT", "8000"))

def load_config() -> "Config":
    return Config()
```

`.env.example` gets committed. It tells the next person which variables exist without ever showing them a real value:

```
# Copy to .env (which git ignores) and fill in real values, or just export them.
DATABASE_URL=postgresql+psycopg2://refapp:REPLACE_ME@127.0.0.1:5432/refapp
APP_NAME=refapp
PORT=8000
```

`.gitignore` keeps the real secrets and the virtualenv out of history:

```
.venv/
.env
*.pyc
__pycache__/
```

## 5. Wire up the database

`refapp/db.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import load_config

Base = declarative_base()

_config = load_config()
engine = create_engine(_config.database_url, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, future=True)
```

`refapp/models.py`, the single row type the feature endpoint stores:

```python
from datetime import datetime, timezone
from sqlalchemy import Integer, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class Order(Base):
    __tablename__ = "orders"

    id:         Mapped[int]      = mapped_column(Integer, primary_key=True)
    item_count: Mapped[int]      = mapped_column(Integer, nullable=False)
    total:      Mapped[float]    = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "item_count": self.item_count,
            "total": str(self.total),
            "created_at": self.created_at.isoformat(),
        }
```

## 6. The math, kept separate from everything else

`refapp/pricing.py` touches no network, no database, no files. That is what makes it trivial to test on its own in Lab 5D:

```python
from decimal import Decimal, ROUND_HALF_UP

TAX_RATE = Decimal("0.13")

def line_total(unit_price: Decimal, quantity: int) -> Decimal:
    if quantity < 0:
        raise ValueError("quantity must not be negative")
    return (unit_price * quantity).quantize(Decimal("0.01"), ROUND_HALF_UP)

def order_total(items: list[tuple[Decimal, int]]) -> Decimal:
    """items is a list of (unit_price, quantity). Returns the tax inclusive total."""
    subtotal = sum((line_total(p, q) for p, q in items), Decimal("0"))
    tax = (subtotal * TAX_RATE).quantize(Decimal("0.01"), ROUND_HALF_UP)
    return subtotal + tax
```

## 7. The counters

`refapp/metrics.py`. Prometheus scrapes plain text, and `prometheus_client` produces it for you:

```python
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

REQUESTS = Counter(
    "refapp_http_requests_total", "HTTP requests", ["method", "endpoint", "status"]
)
ORDERS_CREATED = Counter(
    "refapp_orders_created_total", "Orders written to the database"
)

def render_metrics() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST
```

## 8. The application itself

`refapp/app.py` ties it together. Health actually asks the database if it is there. Metrics reports the counters. `/total` does the pure math with no storage. `/orders` does the real thing: compute, store, and read back.

```python
from decimal import Decimal
from flask import Flask, request, jsonify, Response
from sqlalchemy import text, select
from .config import load_config
from .db import SessionLocal, Base, engine
from .models import Order
from .pricing import order_total
from .metrics import REQUESTS, ORDERS_CREATED, render_metrics

def create_app() -> Flask:
    app = Flask(__name__)
    cfg = load_config()
    app.config["APP_NAME"] = cfg.app_name

    @app.after_request
    def count(resp):
        if request.endpoint:
            REQUESTS.labels(request.method, request.path, resp.status_code).inc()
        return resp

    # Health: is the process up, and can it actually reach the database?
    @app.get("/health")
    def health():
        db_up = True
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception:
            db_up = False
        status = "ok" if db_up else "degraded"
        code = 200 if db_up else 503
        return jsonify(status=status, app=app.config["APP_NAME"],
                       db="up" if db_up else "down"), code

    # Metrics
    @app.get("/metrics")
    def metrics():
        body, content_type = render_metrics()
        return Response(body, mimetype=content_type)

    # Feature one: the pure calculation, no database
    @app.post("/total")
    def total():
        payload = request.get_json(force=True)
        items = [(Decimal(str(i["price"])), int(i["qty"])) for i in payload["items"]]
        return jsonify(total=str(order_total(items)))

    # Feature two: store an order, then read orders back
    @app.post("/orders")
    def create_order():
        payload = request.get_json(force=True)
        items = [(Decimal(str(i["price"])), int(i["qty"])) for i in payload["items"]]
        order = Order(item_count=sum(q for _, q in items), total=order_total(items))
        with SessionLocal() as db:
            db.add(order)
            db.commit()
            db.refresh(order)
            result = order.as_dict()
        ORDERS_CREATED.inc()
        return jsonify(result), 201

    @app.get("/orders")
    def list_orders():
        with SessionLocal() as db:
            # Read this closely in Lab 5D. There is no ORDER BY here on purpose.
            rows = db.execute(select(Order)).scalars().all()
            return jsonify([o.as_dict() for o in rows])

    @app.get("/orders/<int:order_id>")
    def get_order(order_id: int):
        with SessionLocal() as db:
            order = db.get(Order, order_id)
            if order is None:
                return jsonify(error="not found"), 404
            return jsonify(order.as_dict())

    return app

# A quick way to create the table for now. Lab 5E replaces this with a real migration.
def init_db() -> None:
    from . import models
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    application = create_app()
    application.run(host="0.0.0.0", port=load_config().port)
```

Leave `refapp/__init__.py` empty.

## 9. Point it at the database and run it

Export the configuration. None of this is committed anywhere:

```bash
export DATABASE_URL="postgresql+psycopg2://refapp:${PGPASSWORD}@127.0.0.1:5432/refapp"
export APP_NAME="refapp"
export PORT=8000
```

Create the table for now, then start the service. It writes its logs to stdout, the way a service behind a process manager should:

```bash
python -c "from refapp.app import init_db; init_db()"
python -m refapp.app &
```

## 10. Hit every endpoint

```bash
# Health, and notice it reports the real database as up
curl -s localhost:8000/health
# {"app":"refapp","db":"up","status":"ok"}

# The pure calculation. (10.00 times 2) plus (5.50 times 1) is 25.50, plus 13% tax
# of 3.32, which comes to 28.82.
curl -s -X POST localhost:8000/total -H 'Content-Type: application/json' \
     -d '{"items":[{"price":"10.00","qty":2},{"price":"5.50","qty":1}]}'
# {"total":"28.82"}

# Store the same order, then read it straight back
curl -s -X POST localhost:8000/orders -H 'Content-Type: application/json' \
     -d '{"items":[{"price":"10.00","qty":2},{"price":"5.50","qty":1}]}'
# {"created_at":"...","id":1,"item_count":3,"total":"28.82"}
curl -s localhost:8000/orders/1

# Metrics, where you can watch the counters you just moved
curl -s localhost:8000/metrics | grep refapp_
```

And confirm the row really landed in Postgres, not just in the response:

```bash
docker exec -it refapp-db psql -U refapp -d refapp -c "SELECT * FROM orders;"
```

At this point you have a service configured entirely from the environment, storing real data in a real database, with no password anywhere in the code. Leave the container running and keep the folder. Lab 5D puts this under test, and Lab 5E takes the schema away from that quick `init_db` shortcut and hands it to a proper migration.
