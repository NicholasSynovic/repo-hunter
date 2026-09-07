import sys
from pathlib import Path

from loguru import logger
from sqlalchemy import (
    Column,
    Engine,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    event,
)


class DB:
    def __init__(self, db_path: Path) -> None:
        if db_path.exists() and db_path.is_file():
            logger.error(f"{db_path.name} already exists")
            sys.exit(1)

        self._path: Path = db_path
        self.engine: Engine = create_engine(url=f"sqlite:///{self._path}")
        self.metadata: MetaData = MetaData()

        # SQLite enforces foreign keys only when this pragma is enabled per connection
        @event.listens_for(self.engine, "connect")
        def _enable_foreign_keys(dbapi_connection, connection_record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    def create_tables(self) -> None:
        _: Table = Table(
            "awesome_lists",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("projects_url", String),
            Column("repository_url", String),
            Column("json_str", String),
        )

        _ = Table(
            "awesome_list_projects",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("list_id", Integer, ForeignKey("awesome_lists.id")),
            Column("repository_url", String),
            Column("json_str", String),
        )

        self.metadata.create_all(bind=self.engine, checkfirst=True)
        logger.info(f"Created tables in {self._path.name}")
