import os
from argparse import ArgumentParser, Namespace
from pathlib import Path

from joss import APPLICATION_NAME


def create_cli() -> Namespace:
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
        required=required,
        help="SQLite3 database path to write to.",
        type=Path,
    )
    parser.add_argument(
        "--resolve-urls",
        required=required,
        help="Resolve URLs (can take a while)",
        action="store_true",
    )
    return parser.parse_args()
