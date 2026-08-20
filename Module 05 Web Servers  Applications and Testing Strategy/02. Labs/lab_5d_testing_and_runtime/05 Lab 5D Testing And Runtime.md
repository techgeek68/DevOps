# Lab 5D. Testing the Service, Catching a Flake, and Timing the Suite

Now you give `refapp` a test suite with two layers. The fast layer checks the pure math with no database anywhere near it. The slower layer drives the real HTTP endpoints against the containerized Postgres from Lab 5C. Then you meet a test that passes some runs and fails others, work out why, and fix it. Last, you treat the suite's own runtime as something to measure rather than guess at.

That final piece, running the thing several times and reasoning from the numbers you get back, is the part that answers **ABET Student Outcome Six**: developing and running an experiment, reading the data, and drawing a defensible conclusion.

## 1. Add the test tools

Append to `requirements.txt` and install:

```
pytest==8.2.0
pytest-xdist==3.6.1
```

```bash
source ~/refapp/.venv/bin/activate
pip install -r requirements.txt
```

`pytest.ini` in the project root:

```ini
[pytest]
addopts = -q
testpaths = tests
```

## 2. Set up shared fixtures

`tests/conftest.py`. The integration tests point at the real container, and every test starts from an empty table so nothing one test writes can leak into the next. That isolation is not just tidiness: it is what lets the tests run in any order, and later in parallel, without turning on each other.

```python
import pytest
from sqlalchemy import text
from refapp.app import create_app, init_db
from refapp.db import engine

@pytest.fixture(scope="session", autouse=True)
def schema():
    # A quick bootstrap for the test database. Lab 5E swaps this for a migration.
    init_db()

@pytest.fixture(autouse=True)
def clean_table():
    # Empty the table before each test so every test starts from a known place.
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE orders RESTART IDENTITY"))
    yield

@pytest.fixture
def client():
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()
```

## 3. The fast layer: the math on its own

`tests/test_pricing.py`. No database, no server, a few milliseconds each. You can write dozens of these without noticing the cost:

```python
from decimal import Decimal
import pytest
from refapp.pricing import line_total, order_total

def test_line_total_rounds_up_at_the_half():
    assert line_total(Decimal("1.005"), 1) == Decimal("1.01")

def test_order_total_adds_tax():
    items = [(Decimal("10.00"), 2), (Decimal("5.50"), 1)]   # subtotal 25.50
    assert order_total(items) == Decimal("28.82")           # plus 13% tax of 3.32

def test_negative_quantity_is_rejected():
    with pytest.raises(ValueError):
        line_total(Decimal("10.00"), -1)
```

## 4. The slower layer: the endpoints against real Postgres

`tests/test_orders_api.py`. These drive the HTTP layer wired to the database through the fixture:

```python
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
```

Run the whole thing. The math flies; the endpoint tests take longer because they are really talking to Postgres:

```bash
cd ~/refapp
pytest
```

## 5. Meet the flake

Add `tests/test_orders_ordering.py`. Nothing about it looks wrong at first glance:

```python
import json

def _post_order(client, items):
    return client.post("/orders", data=json.dumps({"items": items}),
                       content_type="application/json")

def test_orders_come_back_in_the_order_they_were_made(client):
    _post_order(client, [{"price": "1.00", "qty": 1}])   # made first
    _post_order(client, [{"price": "2.00", "qty": 1}])   # made second
    ids = [o["id"] for o in client.get("/orders").get_json()]
    assert ids == sorted(ids)     # expects ascending. But is that promised anywhere?
```

Run it once and it might pass. Run it twenty times and watch it waver:

```bash
for i in $(seq 1 20); do
  pytest tests/test_orders_ordering.py -q >/dev/null 2>&1 \
    && echo "run $i: PASS" || echo "run $i: FAIL"
done
```

A mix of PASS and FAIL on code that never changed is the whole signature of a flake. This is the moment most teams reach for a retry button. Do not.

## 6. Find out why

The test expects `GET /orders` to hand back rows oldest first. Look again at that endpoint from Lab 5C:

```python
rows = db.execute(select(Order)).scalars().all()   # no ORDER BY
```

Here is the thing SQL never promised you: without an explicit `ORDER BY`, the database can return rows in whatever order suits it. On a fresh little table that often happens to be insertion order, which is why the test passes sometimes, but nothing guarantees it, and under load or after the table has been reorganized the order can shift. So the test is not being fussy. It found a real bug in the application. Telling those two cases apart, a badly written test versus a test exposing a genuine defect, is the judgment this exercise is really about.

## 7. Fix it in the right place

The fix belongs in the application, not in the test. Make the query deterministic. In `refapp/app.py`, change the list query to sort by id:

```python
from sqlalchemy import select
# ...
rows = db.execute(select(Order).order_by(Order.id)).scalars().all()
```

Now run the loop again and watch it hold steady:

```bash
for i in $(seq 1 20); do
  pytest tests/test_orders_ordering.py -q >/dev/null 2>&1 \
    && echo "run $i: PASS" || echo "run $i: FAIL"
done
# You want twenty passes out of twenty.
```

Flakes wear a few other disguises worth recognizing, because the cure is always the same: kill the source of nondeterminism, never paper over it with a retry. Watch for tests that lean on the wall clock or `now()`, tests with unseeded randomness, tests that share mutable state, and tests that reach out to something live on the network.

## 8. Measure how long the suite takes

Guessing at test runtime is how suites quietly bloat to twenty minutes. So measure it, and treat it as an experiment. The question: does running in parallel with `pytest-xdist` actually beat running in sequence? The thing you change is the execution mode. Everything else, the code, the data, the machine, stays put. Run each mode five times and average.

```bash
# Run the whole suite once and print the seconds it took
runtime () { /usr/bin/env bash -c '
  start=$(date +%s.%N); pytest "$@" >/dev/null 2>&1; end=$(date +%s.%N)
  echo "$end - $start" | bc' _ "$@"; }

echo "=== Sequential ==="
for i in $(seq 1 5); do echo "trial $i: $(runtime) s"; done

echo "=== Parallel (-n auto) ==="
for i in $(seq 1 5); do echo "trial $i: $(runtime -n auto) s"; done
```

While you are at it, see where the time actually goes, because that is what tells you what to fix later:

```bash
pytest --durations=10        # the ten slowest tests
```

Write your numbers into a table like this:

| Trial | Sequential (s) | Parallel with -n auto (s) |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |
| Mean | | |

Then read what you got. Average each column, say whether the numbers back the idea that parallel wins, and be honest about the result. On a suite this tiny the cost of spinning up parallel workers can swallow the time it saves, so parallel might actually lose here and only pay off once the suite grows. That is a real conclusion drawn from your own data, which is the point, not a rule copied from somewhere. You will also notice the endpoint tests dominate the clock, because they do real database work. That is exactly why you keep that layer small and the math layer large.

By the end you have a two layer suite that passes, a flaky test you tracked down to a missing `ORDER BY` and fixed in the code, and a short experiment with real timings and a conclusion you can defend. Keep everything. Lab 5E changes how the schema gets created and asks these same tests to keep passing.
