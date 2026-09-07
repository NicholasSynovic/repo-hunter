import os
from argparse import ArgumentParser, Namespace
from pathlib import Path

from joss import APPLICATION_NAME
from joss.db import DB
from joss.extract import Extract
from joss.load import Load
from joss.models import JOSSGHIssue, JOSSPaperProjectIssue
from joss.transform import Transform


def setup_db(db_path: Path) -> DB:
    db: DB = DB(db_path=db_path)
    db.create_tables()
    return db


def extract_issues(github_token: str) -> list[JOSSGHIssue]:
    pipeline_step: Extract = Extract(github_token=github_token)
    return pipeline_step.extract()


def transform_issues(data: list[JOSSGHIssue]) -> list[JOSSPaperProjectIssue]:
    pipeline_step: Transform = Transform()
    return pipeline_step.transform(data=data)


def load_issues(
    issues: list[JOSSGHIssue],
    ppi: list[JOSSPaperProjectIssue],
    db: DB,
) -> None:
    pipeline_step: Load = Load(db=db)
    pipeline_step.load_data(issues=issues, ppi=ppi)


if __name__ == "__main__":
    github_token: str | None = os.getenv("GITHUB_TOKEN")

    parser: ArgumentParser = ArgumentParser(
        prog=APPLICATION_NAME,
        description="A command-line toolkit for building local SQLite datasets from open-source repository ecosystems.",
        epilog="Created by Nicholas M. Synovic",
    )
    parser.add_argument(
        "-g",
        "--github-token",
        default=github_token,
        required=github_token is None,
        help="GitHub personal access token",
    )
    parser.add_argument(
        "-o",
        "--out-file",
        required=True,
        help="SQLite3 database path to write to.",
        type=lambda x: Path(x).absolute(),
    )
    parser.add_argument(
        "--resolve-urls",
        required=False,
        help="Resolve URLs (can take a while)",
        action="store_true",
    )
    args: Namespace = parser.parse_args()

    # Setup database tables
    db: DB = setup_db(db_path=args.out_file)

    # Extract issues from GitHub
    issues: list[JOSSGHIssue] = extract_issues(github_token=args.github_token)

    # Transform issues from GitHub
    ppi: list[JOSSPaperProjectIssue] = transform_issues(data=issues)

    # Load data into the database
    load_issues(issues=issues, ppi=ppi, db=db)
