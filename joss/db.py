from pathlib import Path

from sqlalchemy import (
    Boolean,
    Column,
    Engine,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
)


class DB:
    def __init__(self, db_path: Path) -> None:
        self._path: Path = db_path

        self.engine: Engine = create_engine(url=f"sqlite:///{self._path}")
        self.metadata: MetaData = MetaData()

    def create_tables(self) -> None:
        _: Table = Table(
            "joss_issues",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("github_issue_id", Integer),
            Column("is_pull_request", Boolean),
            Column("body", String),
            Column("creator", String),
            Column("state", String),
            Column("labels", String),
            Column("json", String),
        )

        self.metadata.create_all(bind=self.engine, checkfirst=True)
