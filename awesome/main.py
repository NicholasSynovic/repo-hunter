from argparse import ArgumentParser, Namespace
from pathlib import Path

from awesome import APPLICATION_NAME
from awesome.db import DB
from awesome.etl import AwesomeList, ListProject
from awesome.etl.extract import Extract
from awesome.etl.load import Load
from awesome.etl.transform import Transform


def setup_db(db_path: Path) -> DB:
    db: DB = DB(db_path=db_path)
    db.create_tables()
    return db


def extract_lists(email: str) -> list[AwesomeList]:
    pipeline_step: Extract = Extract(email=email)
    return pipeline_step.extract()


def transform_lists(data: list[AwesomeList], email: str) -> list[ListProject]:
    pipeline_step: Transform = Transform(email=email)
    return pipeline_step.transform(data=data)


def load_lists(
    lists: list[AwesomeList],
    projects: list[ListProject],
    db: DB,
) -> None:
    pipeline_step: Load = Load(db=db)
    pipeline_step.load_data(lists=lists, projects=projects)


if __name__ == "__main__":
    parser: ArgumentParser = ArgumentParser(
        prog=APPLICATION_NAME,
        description="A command-line toolkit for building local SQLite datasets from open-source repository ecosystems.",
        epilog="Created by Nicholas M. Synovic",
    )
    parser.add_argument(
        "-o",
        "--out-file",
        required=True,
        help="SQLite3 database path to write to.",
        type=lambda x: Path(x).absolute(),
    )
    parser.add_argument(
        "--email",
        required=True,
        help="Contact email sent to the Ecosyste.ms Awesome API mailto parameter.",
    )
    args: Namespace = parser.parse_args()

    # Setup database tables
    db: DB = setup_db(db_path=args.out_file)

    # Extract lists from the Awesome API
    lists: list[AwesomeList] = extract_lists(email=args.email)

    # Transform lists into list projects
    projects: list[ListProject] = transform_lists(data=lists, email=args.email)

    # Load data into the database
    load_lists(lists=lists, projects=projects, db=db)
