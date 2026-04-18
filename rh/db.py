from logging import Logger
from pathlib import Path

from joss.logger import JOSSLogger
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


class DB:
    def __init__(self, joss_logger: JOSSLogger, db_path: Path) -> None:
        self._path: Path = db_path.absolute()

        self.engine: Engine = create_engine(url=f"sqlite:///{self._path}")
        self.logger: Logger = joss_logger.get_logger()
        self.metadata: MetaData = MetaData()

        self._create_tables()

    def _create_tables(self) -> None:
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
