import json

def _post_order(client, items):
    return client.post("/orders", data=json.dumps({"items": items}),
                       content_type="application/json")

def test_creating_an_order_stores_it(client):
    resp = _post_order(client, [{"price": "10.00", "qty": 2},
                                {"price": "5.50", "qty": 1}])
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["total"] == "28.82"
    assert body["item_count"] == 3

def test_reading_an_order_back(client):
    created = _post_order(client, [{"price": "3.00", "qty": 4}]).get_json()
    fetched = client.get(f"/orders/{created['id']}").get_json()
    assert fetched == created

def test_health_sees_the_database(client):
    body = client.get("/health").get_json()
    assert body["db"] == "up"
