import sys
from pathlib import Path

from loguru import logger
from sqlalchemy import (
    Boolean,
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

    def create_tables(self, dataset: str) -> None:
        if dataset == "joss":
            _: Table = Table(
                "joss_github_issues",
                self.metadata,
                Column("id", Integer, primary_key=True),
                Column("labels", String),
                Column("body", String),
                Column("creator", String),
                Column("state", String),
                Column("json_str", String),
            )

            _ = Table(
                "joss_paper_project_issues",
                self.metadata,
                Column("id", Integer, primary_key=True),
                Column("github_issue_id", Integer, ForeignKey("joss_github_issues.id")),
                Column("github_repo_url", String),
                Column("joss_url", String),
                Column("joss_resolved_url", String),
            )

        elif dataset == "awesome":
            _: Table = Table(
                "awesome_lists",
                self.metadata,
                Column("id", Integer, primary_key=True),
                Column("url", String),
                Column("name", String),
                Column("description", String),
                Column("projects_count", Integer),
                Column("stars", Integer),
                Column("primary_language", String),
                Column("list_of_lists", Boolean),
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
