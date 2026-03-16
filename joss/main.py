"""Entry point for the unified ``joss`` command-line application."""

# Copyright (c) 2025 Nicholas M. Synovic

import sys

from joss import APPLICATION_NAME
from joss.cli import CLI
from joss.db import DB
from joss.ecosystems.papers.runner import JOSSRunner as PapersRunner
from joss.joss.runner import JOSSRunner
from joss.logger import JOSSLogger


def main() -> int:
    """Entry point for the JOSS CLI application."""
    args = CLI().run()

    if args.dataset is None:
        sys.exit(1)

    logger: JOSSLogger = JOSSLogger(name=__name__)
    logger.setup_file_logging(prefix=APPLICATION_NAME)

    if args.dataset == "joss":
        resolve_urls: bool = args.resolve_urls
        db: DB = DB(joss_logger=logger, db_path=args.out_file)
        JOSSRunner(joss_logger=logger, db=db, resolve_urls=resolve_urls).run()

    elif args.dataset == "papers":
        db = DB(joss_logger=logger, db_path=args.out_file)
        PapersRunner(
            joss_logger=logger,
            db=db,
            email=args.email,
        ).run()

    else:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
