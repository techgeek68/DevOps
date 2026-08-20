import os
from decimal import Decimal
from flask import Flask, request, jsonify
from .pricing import order_total

def create_app() -> Flask:
    app = Flask(__name__)
    # Configuration comes from the environment, never hard-coded
    app.config["GREETING"] = os.environ.get("GREETING", "Reference App")
    app.config["PORT"]     = int(os.environ.get("PORT", "8000"))

    @app.get("/health")
    def health():
        return jsonify(status="ok", app=app.config["GREETING"])

    @app.post("/total")
    def total():
        payload = request.get_json(force=True)
        items = [(Decimal(str(i["price"])), int(i["qty"])) for i in payload["items"]]
        return jsonify(total=str(order_total(items)))

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=app.config["PORT"])  # logs go to stdout
