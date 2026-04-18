"""Database bootstrap and schema registration utilities."""

# Copyright (c) 2025 Nicholas M. Synovic

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
    """
    SQLite database wrapper used by ETL loaders.

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
        _: Table = Table(  # Table to track application runs
            "_runs",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("subparser", String),
            Column("started_at_unix", Integer),
            Column("finished_at_unix", Integer),
            Column("status", String),
            Column("resolve_urls", Boolean),
            Column("issues_fetched_count", Integer),
            Column("issues_written_count", Integer),
            Column("paper_project_rows_count", Integer),
            Column("error_message", String),
        )

        _: Table = Table(  # Table to store JOSS Github Issues
            "_joss_snapshots",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("run_id", Integer, ForeignKey("_runs.id")),
            Column("joss_github_issue_id", Integer),
            Column("is_pull_request", Boolean),
            Column("body", String),
            Column("creator", String),
            Column("state", String),
            Column("labels", String),
            Column("json_str", String),
            Column("snapshot_at_unix", Integer),
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
