"""Entry point for the standalone JOSS ``joss`` command."""

# Copyright (c) 2025 Nicholas M. Synovic

import sys

from joss.cli import APPLICATION_NAME, CLI
from joss.db import DB
from joss.logger import JOSSLogger
from joss.runner import JOSSRunner


def main() -> int:
    """Entry point for the JOSS CLI application."""
    args = CLI().run()

    logger: JOSSLogger = JOSSLogger(name=__name__)
    logger.setup_file_logging(prefix=APPLICATION_NAME)

    resolve_urls: bool = args.resolve_urls
    db: DB = DB(joss_logger=logger, db_path=args.out_file)
    JOSSRunner(joss_logger=logger, db=db, resolve_urls=resolve_urls).run()

    sys.exit(0)


if __name__ == "__main__":
    main()
