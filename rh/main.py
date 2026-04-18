"""Entry point for the unified ``joss`` command-line application."""

# Copyright (c) 2025 Nicholas M. Synovic

import sys

from rh import APPLICATION_NAME
from rh.cli import CLI
from rh.db import DB
from rh.ecosystems.awesome.runner import JOSSRunner as AwesomeRunner
from rh.ecosystems.papers.runner import JOSSRunner as PapersRunner
from rh.joss.runner import JOSSRunner
from rh.logger import JOSSLogger


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

    elif args.dataset == "awesome":
        db = DB(joss_logger=logger, db_path=args.out_file)
        AwesomeRunner(
            joss_logger=logger,
            db=db,
            email=args.email,
        ).run()

    elif args.dataset == "gh":
        logger.get_logger().info(
            "GitHub repository search is not implemented yet. "
            "Received filters: stars=%d forks=%d watchers=%d issues=%d "
            "age_months=%d prs=%d",
            args.star_count,
            args.fork_count,
            args.watcher_count,
            args.issue_count,
            args.age_months,
            args.pr_count,
        )

    else:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
