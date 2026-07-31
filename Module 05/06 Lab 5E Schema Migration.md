# Lab 5E. Handing the Schema to Migrations

Up to now the `orders` table has been created by a shortcut: that little `init_db` call in Lab 5C, and the same call in the test fixtures in Lab 5D. It works, but it has no memory. It cannot tell you what changed, and it cannot walk a change backwards. This lab replaces it with a migration tool, writes the very first migration, and proves you can roll it forward and back.

That last part matters more than it looks. A migration you can apply and then undo is what makes a schema change reversible, and reversible rollback is the whole foundation Module 15 builds on. The migration you commit here is the first stone in that wall.

The tool is Alembic, which is the migration framework built for SQLAlchemy.

## 1. Add Alembic

Append to `requirements.txt` and install:

```
alembic==1.13.2
```

```bash
source ~/refapp/.venv/bin/activate
cd ~/refapp
pip install -r requirements.txt
```

## 2. Set it up

```bash
alembic init migrations
```

That creates `alembic.ini` and a `migrations/` folder holding an `env.py` and a `versions/` directory where each migration script will live.

## 3. Make Alembic read the environment, not a config file

Out of the box, Alembic wants the database URL written into `alembic.ini`. That would put credentials in a committed file, which is the one thing Lab 5C told you never to do. So you pull the URL from the environment instead, and point Alembic at the application's own model definitions.

First, blank out the static URL line in `alembic.ini` so nothing sensitive gets committed:

```ini
# Leave this empty. env.py fills it in from the environment.
sqlalchemy.url =
```

Then open `migrations/env.py` and, just below the existing imports near the top, add:

```python
import os
from refapp.db import Base
from refapp import models  # importing this registers the Order model on Base

# The URL comes from the environment, never from the file
config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

# This is what Alembic compares the database against when autogenerating
target_metadata = Base.metadata
```

Find the line in `env.py` that reads `target_metadata = None` and delete it. The assignment you just added takes its place.

## 4. Write the first migration

You want this migration to be the thing that creates the table, so let Alembic compare your models against an empty database and generate the difference. That means dropping the table the Lab 5C and 5D shortcut left behind, so Alembic sees a clean slate:

```bash
export DATABASE_URL="postgresql+psycopg2://refapp:${PGPASSWORD}@127.0.0.1:5432/refapp"

# Clear the shortcut's table so the migration is the real source of truth
docker exec -it refapp-db psql -U refapp -d refapp -c "DROP TABLE IF EXISTS orders;"

alembic revision --autogenerate -m "create orders table"
```

Open the new file under `migrations/versions/`. Look at its two functions and notice they mirror each other. `upgrade` builds the table, `downgrade` tears it down. That symmetry is the reversibility, made concrete:

```python
def upgrade():
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("item_count", sa.Integer(), nullable=False),
        sa.Column("total", sa.Numeric(10, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

def downgrade():
    op.drop_table("orders")
```

## 5. Apply it, then prove it goes both ways

```bash
alembic upgrade head          # run the migration, the orders table appears
docker exec -it refapp-db psql -U refapp -d refapp -c "\d orders"

alembic current              # which revision is applied right now
alembic history --verbose    # the chain of migrations so far
```

Now the part that rehearses what Module 15 leans on. Roll back one step and watch the table vanish, then roll forward and watch it return:

```bash
alembic downgrade -1         # step back one revision, orders is dropped
docker exec -it refapp-db psql -U refapp -d refapp -c "\dt"   # orders is gone

alembic upgrade head         # step forward again, orders is back
```

## 6. Retire the shortcut

The migration owns the schema now, so pull out the old `init_db` before the two ways of building the table drift apart.

In `refapp/app.py`, delete the `init_db` function and the call to it in the `__main__` block. From here on the table exists because you ran `alembic upgrade head` before starting the app.

In `tests/conftest.py`, replace the bootstrap fixture so the test database is brought up and torn down by Alembic:

```python
import subprocess
import pytest

@pytest.fixture(scope="session", autouse=True)
def schema():
    # The migration owns the schema. Bring the test database to head, then clean up.
    subprocess.run(["alembic", "upgrade", "head"], check=True)
    yield
    subprocess.run(["alembic", "downgrade", "base"], check=True)
```

Run the Lab 5D suite one more time and confirm nothing broke now that migrations are in charge:

```bash
alembic upgrade head
pytest
```

## 7. Commit it

The migration is source code and belongs in version control. The empty `.env`, the real secrets, and the virtualenv do not, and your `.gitignore` from Lab 5C already keeps them out.

```bash
cd ~/refapp
git init 2>/dev/null || true
git add refapp/ tests/ migrations/ alembic.ini requirements.txt pytest.ini \
        .env.example .gitignore
git status                      # look hard: no .env, no .venv, no real credentials
git commit -m "Add first schema migration: create orders table"
```

The schema now moves forward and back through numbered, reversible steps. When Module 15 walks you through rolling a bad change back out of production, this first migration is the baseline it assumes you already have. You just built it.
