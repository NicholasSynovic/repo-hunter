"""Entry point for the unified ``joss`` command-line application."""

# Copyright (c) 2025 Nicholas M. Synovic

import sys

from rh import APPLICATION_NAME
from rh.cli import CLI
from rh.db import DB
from rh.ecosystems.awesome.runner import JOSSRunner as AwesomeRunner
from rh.ecosystems.papers.runner import JOSSRunner as PapersRunner
from rh.gh.api import GitHubGraphQLAPI
from rh.joss.runner import JOSSRunner
from rh.logger import JOSSLogger


def main() -> int:
    """Entry point for the JOSS CLI application."""
    args = CLI().run()

    logger: JOSSLogger = JOSSLogger(name=__name__)
    logger.setup_file_logging(prefix=APPLICATION_NAME)

    if args.dataset == "awesome":
        db = DB(joss_logger=logger, db_path=args.out_file)
        AwesomeRunner(
            joss_logger=logger,
            db=db,
            email=args.email,
        ).run()

    elif args.dataset == "gh":
        token: str = CLI.get_token()
        gh_api: GitHubGraphQLAPI = GitHubGraphQLAPI(
            token=token,
            logger=logger.get_logger(),
        )
        payload: dict[str, object] = gh_api.build_query(
            star_count=args.star_count,
            fork_count=args.fork_count,
            watcher_count=args.watcher_count,
            issue_count=args.issue_count,
            age_months=args.age_months,
            pr_count=args.pr_count,
        )
        data: dict = gh_api.execute_query(payload=payload)
        logger.get_logger().info(
            "GitHub repository search is not implemented yet. "
            "Received filters: stars=%s forks=%s watchers=%s issues=%s "
            "age_months=%s prs=%s. repositoryCount=%s",
            args.star_count,
            args.fork_count,
            args.watcher_count,
            args.issue_count,
            args.age_months,
            args.pr_count,
            data.get("data", {}).get("search", {}).get("repositoryCount"),
        )

    elif args.dataset == "joss":
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
