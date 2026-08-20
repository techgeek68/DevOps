import json
from refapp.app import create_app

def client():
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()

def test_total_endpoint_returns_tax_inclusive_total():
    resp = client().post(
        "/total",
        data=json.dumps({"items": [{"price": "10.00", "qty": 2},
                                    {"price": "5.50", "qty": 1}]}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert resp.get_json()["total"] == "28.82"

def test_health_reads_config_from_env(monkeypatch):
    monkeypatch.setenv("GREETING", "IntegrationEnv")
    resp = client().get("/health")
    assert resp.get_json()["app"] == "IntegrationEnv"   # config truly from env
