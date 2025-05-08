from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.provider_interface import AbstractDatabaseProvider


class PostgresProvider(AbstractDatabaseProvider):
    def __init__(
        self,
        user: str,
        password: str,
        db: str,
        host: str = "postgres",
        port: int = 5432,
    ):
        self.url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
        self.engine = create_engine(self.url, future=True)
        self.session = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)

    def get_session(self):
        return self.session()
