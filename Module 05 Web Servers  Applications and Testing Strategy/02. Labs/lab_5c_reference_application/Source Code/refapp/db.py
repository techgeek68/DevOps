from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import load_config

Base = declarative_base()

_config = load_config()
engine = create_engine(_config.database_url, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, future=True)
