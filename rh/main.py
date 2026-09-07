import os
from argparse import ArgumentParser, Namespace
from pathlib import Path

from rh import APPLICATION_NAME
from rh.db import DB
from rh.etl.awesome import AwesomeList, ListProject
from rh.etl.awesome.extract import Extract as AwesomeExtract
from rh.etl.awesome.load import Load as AwesomeLoad
from rh.etl.awesome.transform import Transform as AwesomeTransform
from rh.etl.joss import JOSSGHIssue, JOSSPaperProjectIssue
from rh.etl.joss.extract import Extract as JOSSExtract
from rh.etl.joss.load import Load as JOSSLoad
from rh.etl.joss.transform import Transform as JOSSTransform


def setup_db(db_path: Path, dataset: str) -> DB:
    db: DB = DB(db_path=db_path)
    db.create_tables(dataset=dataset)
    return db


def extract_issues(github_token: str) -> list[JOSSGHIssue]:
    pipeline_step: JOSSExtract = JOSSExtract(github_token=github_token)
    return pipeline_step.extract()


def transform_issues(
    data: list[JOSSGHIssue],
    resolve_urls: bool,
) -> list[JOSSPaperProjectIssue]:
    pipeline_step: JOSSTransform = JOSSTransform(resolve_joss_url=resolve_urls)
    return pipeline_step.transform(data=data)


def load_issues(
    issues: list[JOSSGHIssue],
    ppi: list[JOSSPaperProjectIssue],
    db: DB,
) -> None:
    pipeline_step: JOSSLoad = JOSSLoad(db=db)
    pipeline_step.load_data(issues=issues, ppi=ppi)


def extract_lists(email: str) -> list[AwesomeList]:
    pipeline_step: AwesomeExtract = AwesomeExtract(email=email)
    return pipeline_step.extract()


def transform_lists(
    data: list[AwesomeList],
    email: str,
) -> list[ListProject]:
    pipeline_step: AwesomeTransform = AwesomeTransform(email=email)
    return pipeline_step.transform(data=data)


def load_lists(
    lists: list[AwesomeList],
    projects: list[ListProject],
    db: DB,
) -> None:
    pipeline_step: AwesomeLoad = AwesomeLoad(db=db)
    pipeline_step.load_data(lists=lists, projects=projects)


def main() -> int:
    github_token: str | None = os.getenv("GITHUB_TOKEN")

    parser: ArgumentParser = ArgumentParser(
        prog=APPLICATION_NAME,
        description="A command-line toolkit for building local SQLite datasets from open-source repository ecosystems.",
        epilog="Created by Nicholas M. Synovic",
    )
    subparsers = parser.add_subparsers(dest="dataset", required=True)

    joss_parser: ArgumentParser = subparsers.add_parser(
        "joss",
        help="Collect all Journal of Open Source Software (JOSS) review issues.",
    )
    joss_parser.add_argument(
        "-g",
        "--github-token",
        default=github_token,
        required=github_token is None,
        help="GitHub personal access token",
    )
    joss_parser.add_argument(
        "-o",
        "--out-file",
        required=True,
        help="SQLite3 database path to write to.",
        type=lambda x: Path(x).absolute(),
    )
    joss_parser.add_argument(
        "--resolve-urls",
        required=False,
        help="Resolve URLs (can take a while)",
        action="store_true",
    )

    awesome_parser: ArgumentParser = subparsers.add_parser(
        "awesome",
        help="Collect Ecosyste.ms Awesome lists and their projects.",
    )
    awesome_parser.add_argument(
        "-o",
        "--out-file",
        required=True,
        help="SQLite3 database path to write to.",
        type=lambda x: Path(x).absolute(),
    )
    awesome_parser.add_argument(
        "--email",
        required=True,
        help="Contact email sent to the Ecosyste.ms Awesome API mailto parameter.",
    )
    args: Namespace = parser.parse_args()

    # Setup database tables
    db: DB = setup_db(db_path=args.out_file, dataset=args.dataset)

    if args.dataset == "joss":
        # Extract issues from GitHub
        issues: list[JOSSGHIssue] = extract_issues(github_token=args.github_token)

        # Transform issues from GitHub
        ppi: list[JOSSPaperProjectIssue] = transform_issues(
            data=issues,
            resolve_urls=args.resolve_urls,
        )

        # Load data into the database
        load_issues(issues=issues, ppi=ppi, db=db)

    elif args.dataset == "awesome":
        # Extract lists from the Awesome API
        lists: list[AwesomeList] = extract_lists(email=args.email)

        # Transform lists into list projects
        projects: list[ListProject] = transform_lists(data=lists, email=args.email)

        # Load data into the database
        load_lists(lists=lists, projects=projects, db=db)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
