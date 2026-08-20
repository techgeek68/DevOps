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
