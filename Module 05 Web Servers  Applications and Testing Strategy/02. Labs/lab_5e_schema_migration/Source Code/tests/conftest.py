import subprocess
import pytest

@pytest.fixture(scope="session", autouse=True)
def schema():
    # The migration owns the schema. Bring the test database to head, then clean up.
    subprocess.run(["alembic", "upgrade", "head"], check=True)
    yield
    subprocess.run(["alembic", "downgrade", "base"], check=True)
