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
