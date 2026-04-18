"""Database bootstrap and schema registration utilities."""

from logging import Logger
from pathlib import Path

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
)

from rh.logger import JOSSLogger


class DB:
    """SQLite database wrapper used by ETL loaders.

    Parameters
    ----------
    joss_logger : JOSSLogger
        Logger wrapper used to obtain the shared application logger.
    db_path : Path
        Path to the SQLite database file.
    """

    def __init__(self, joss_logger: JOSSLogger, db_path: Path) -> None:
        """Initialize the database engine and ensure tables exist."""
        self._path: Path = db_path.absolute()

        self.engine: Engine = create_engine(url=f"sqlite:///{self._path}")
        self.logger: Logger = joss_logger.get_logger()
        self.metadata: MetaData = MetaData()

        self._create_tables()

    def _create_tables(self) -> None:
        """Create all expected tables when they do not already exist."""
        _: Table = Table(
            "_joss_github_issues",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("is_pull_request", Boolean),
            Column("body", String),
            Column("creator", String),
            Column("state", String),
            Column("labels", String),
            Column("json_str", String),
        )

        _: Table = Table(
            "_joss_paper_project_issues",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column(
                "joss_github_issue_id",
                Integer,
                ForeignKey("_joss_github_issues.id"),
            ),
            Column("github_repo_url", String),
            Column("joss_url", String),
            Column("joss_resolved_url", String),
            Column("journal", String),
        )

        _: Table = Table(
            "_ecosystems_projects",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("project_url", String),
            Column("repository_url", String),
            Column("json_str", String),
        )

        _: Table = Table(
            "_ecosystems_mentions",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("project_url", String),
            Column("doi", String),
        )

        self.metadata.create_all(bind=self.engine, checkfirst=True)
