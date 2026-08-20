import json

def _post_order(client, items):
    return client.post("/orders", data=json.dumps({"items": items}),
                       content_type="application/json")

def test_orders_come_back_in_the_order_they_were_made(client):
    _post_order(client, [{"price": "1.00", "qty": 1}])   # made first
    _post_order(client, [{"price": "2.00", "qty": 1}])   # made second
    ids = [o["id"] for o in client.get("/orders").get_json()]
    assert ids == sorted(ids)     # expects ascending. But is that promised anywhere?
