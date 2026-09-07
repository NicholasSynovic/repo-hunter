from argparse import ArgumentParser, Namespace
from pathlib import Path

from awesome import APPLICATION_NAME
from awesome.db import DB
from awesome.etl.extract import AwesomeExtract
from awesome.etl.load import AwesomeLoad
from awesome.etl.transform import AwesomeTransform
from awesome.logger import AwesomeLogger


def setup_db(logger: AwesomeLogger, db_path: Path) -> DB:
    return DB(logger=logger, db_path=db_path)


def extract_data(logger: AwesomeLogger, email: str) -> list[dict[str, list[dict]]]:
    pipeline_step: AwesomeExtract = AwesomeExtract(logger=logger, email=email)
    return pipeline_step.download_data()


def transform_data(logger: AwesomeLogger, data: list[dict]) -> dict[str, list]:
    pipeline_step: AwesomeTransform = AwesomeTransform(logger=logger)
    return pipeline_step.transform_data(data=data)


def load_data(logger: AwesomeLogger, data: dict[str, list], db: DB) -> bool:
    pipeline_step: AwesomeLoad = AwesomeLoad(logger=logger, db=db)
    return pipeline_step.load_data(data=data)


def main() -> int:
    parser: ArgumentParser = ArgumentParser(
        prog=APPLICATION_NAME,
        description="Collect list and project data from the Ecosyste.ms Awesome API.",
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
        help="Contact email sent to the Awesome API mailto parameter.",
    )
    args: Namespace = parser.parse_args()

    # Setup file logging
    logger: AwesomeLogger = AwesomeLogger(name=__name__)
    logger.setup_file_logging(prefix=APPLICATION_NAME)

    # Setup database tables
    db: DB = setup_db(logger=logger, db_path=args.out_file)

    # Extract data from the Awesome API
    data: list[dict[str, list[dict]]] = extract_data(logger=logger, email=args.email)

    # Transform data into table-keyed row mappings
    normalized_data: dict[str, list] = transform_data(logger=logger, data=data)

    # Load data into the database
    load_data(logger=logger, data=normalized_data, db=db)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
