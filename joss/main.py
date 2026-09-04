"""Entry point for the standalone JOSS ``joss`` command."""

# Copyright (c) 2025 Nicholas M. Synovic

import os
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from joss import APPLICATION_NAME
from joss.cli import APPLICATION_NAME
from joss.db import DB
from joss.runner import JOSSRunner


def main(args: Namespace) -> int:
    resolve_urls: bool = args.resolve_urls
    db: DB = DB(joss_logger=logger, db_path=args.out_file)
    JOSSRunner(joss_logger=logger, db=db, resolve_urls=resolve_urls).run()

    sys.exit(0)


if __name__ == "__main__":
    github_token: str | None = os.getenv("GITHUB_TOKEN")

    parser: ArgumentParser = ArgumentParser(
        prog=APPLICATION_NAME,
        description="",
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

    main(args=parser.parse_args())
