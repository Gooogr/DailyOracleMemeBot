import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.db_interface import AbstractDatabaseProvider

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
db = os.getenv("POSTGRES_DB")
db_url = f"postgresql+psycopg2://{user}:{password}@postgres:5432/{db}"
engine = create_engine(db_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class PostgresDatabaseProvider(AbstractDatabaseProvider):
    def get_session(self):
        return SessionLocal()

