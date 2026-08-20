import os
from refapp.db import Base
from refapp import models  # importing this registers the Order model on Base

# The URL comes from the environment, never from the file
config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

# This is what Alembic compares the database against when autogenerating
target_metadata = Base.metadata
