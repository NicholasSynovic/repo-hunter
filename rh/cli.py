"""CLI argument helpers for the unified JOSS command."""

# Copyright (c) 2025 Nicholas M. Synovic

import argparse
import os
from argparse import ArgumentParser, Namespace
from pathlib import Path

from rh import APPLICATION_NAME


class CLI:
    """Reusable argument definitions for JOSS sub-commands."""

    @staticmethod
    def parse_filter_count(value: str) -> int:
        """
        Parse a repository filter count allowing ``-1`` as a sentinel.

        Parameters
        ----------
        value : str
            Raw argument value provided on the command line.

        Returns
        -------
        int
            Parsed integer value.

        Raises
        ------
        argparse.ArgumentTypeError
            If ``value`` is not an integer or is less than ``-1``.

        """
        try:
            parsed: int = int(value)
        except ValueError as exc:
            msg = f"Expected an integer value, got: {value}"
            raise argparse.ArgumentTypeError(msg) from exc

        if parsed < -1:
            msg = f"Value must be >= -1, got: {parsed}"
            raise argparse.ArgumentTypeError(msg)

        return parsed

    @staticmethod
    def add_max_pages_argument(parser: argparse.ArgumentParser) -> None:
        """
        Add the ``--max-pages`` optional argument to a parser.

        Parameters
        ----------
        parser : argparse.ArgumentParser
            Argument parser to augment.

        """
        parser.add_argument(
            "--max-pages",
            type=int,
            default=None,
            help=("Maximum number of pages to fetch (for testing). Default: no limit."),
        )

    @staticmethod
    def add_in_file_argument(
        parser: argparse.ArgumentParser,
        *,
        required: bool = True,
    ) -> None:
        """
        Add the ``--in-file`` argument to a parser.

        Parameters
        ----------
        parser : argparse.ArgumentParser
            Argument parser to augment.
        required : bool, default=True
            Whether the argument is mandatory.

        """
        parser.add_argument(
            "-i",
            "--in-file",
            required=required,
            help="Path to input JSON file containing array of GitHub issues.",
        )

    @staticmethod
    def add_out_file_argument(
        parser: argparse.ArgumentParser,
        *,
        required: bool = True,
    ) -> None:
        """
        Add the ``--our-file`` argument to a parser.

        Parameters
        ----------
        parser : argparse.ArgumentParser
            Argument parser to augment.
        required : bool, default=True
            Whether the argument is mandatory.

        """
        parser.add_argument(
            "-o",
            "--out-file",
            required=required,
            help="SQLite3 database path to write to.",
            type=Path,
        )

    @staticmethod
    def add_email_argument(
        parser: argparse.ArgumentParser,
        *,
        required: bool = True,
    ) -> None:
        """
        Add the ``--email`` argument to a parser.

        Parameters
        ----------
        parser : argparse.ArgumentParser
            Argument parser to augment.
        required : bool, default=True
            Whether the argument is mandatory.

        """
        parser.add_argument(
            "--email",
            required=required,
            help="Contact email sent to the Ecosyste.ms API mailto parameter.",
            type=str,
        )

    @staticmethod
    def add_resolve_urls_flag(
        parser: argparse.ArgumentParser,
        *,
        required: bool = False,
    ) -> None:
        """
        Add the ``--resolve-urls`` argument to a parser.

        Parameters
        ----------
        parser : argparse.ArgumentParser
            Argument parser to augment.
        required : bool, default=False
            Whether the argument is mandatory.

        """
        parser.add_argument(
            "--resolve-urls",
            required=required,
            help="Resolve URLs (can take a while)",
            action="store_true",
        )

    @staticmethod
    def get_token() -> str:
        """
        Read `GITHUB_TOKEN` from the environment.

        Returns
        -------
        str
            GitHub token read from ``GITHUB_TOKEN``.

        Raises
        ------
        RuntimeError
            If ``GITHUB_TOKEN`` is missing or empty.

        """
        token: str = os.environ.get("GITHUB_TOKEN", "").strip()
        if not token:
            msg = (
                "Missing GITHUB_TOKEN environment variable.\n"
                "Set it before running, e.g.:\n"
                "  export GITHUB_TOKEN='ghp_...'\n"
                "or (PowerShell):\n"
                '  setx GITHUB_TOKEN "ghp_..."'
            )
            raise RuntimeError(msg)
        return token

    def run(self) -> Namespace:
        """
        Build and run the CLI argument parser.

        Returns
        -------
        Namespace
            Parsed command-line arguments.

        """
        # Setup top level parser
        parser = ArgumentParser(
            prog=APPLICATION_NAME,
            description=f"{APPLICATION_NAME} dataset toolkit.",
        )

        # Setup subparser handler
        subparsers = parser.add_subparsers(
            dest="dataset",
        )

        # Create ingest subparser
        ingest_parser = subparsers.add_parser(
            "joss",
            help="Get all Journal of Open Source Software (JOSS) projects.",
        )
        self.add_out_file_argument(parser=ingest_parser, required=True)
        self.add_resolve_urls_flag(parser=ingest_parser, required=False)

        papers_parser = subparsers.add_parser(
            "papers",
            help="Get all Ecosyste.ms Papers projects.",
        )
        self.add_out_file_argument(parser=papers_parser, required=True)
        self.add_email_argument(parser=papers_parser, required=True)

        awesome_parser = subparsers.add_parser(
            "awesome",
            help="Get all Ecosyste.ms Awesome projects.",
        )
        self.add_out_file_argument(parser=awesome_parser, required=True)
        self.add_email_argument(parser=awesome_parser, required=True)

        gh_parser = subparsers.add_parser(
            "gh",
            help="Search GitHub repositories using configurable thresholds.",
        )
        gh_parser.add_argument(
            "--star-count",
            type=self.parse_filter_count,
            default=-1,
            help="Minimum star count filter. Use -1 to disable.",
        )
        gh_parser.add_argument(
            "--fork-count",
            type=self.parse_filter_count,
            default=-1,
            help="Minimum fork count filter. Use -1 to disable.",
        )
        gh_parser.add_argument(
            "--watcher-count",
            type=self.parse_filter_count,
            default=-1,
            help="Minimum watcher count filter. Use -1 to disable.",
        )
        gh_parser.add_argument(
            "--issue-count",
            type=self.parse_filter_count,
            default=-1,
            help="Minimum issue count filter. Use -1 to disable.",
        )
        gh_parser.add_argument(
            "--age-months",
            type=self.parse_filter_count,
            default=-1,
            help="Maximum repository age in months. Use -1 to disable.",
        )
        gh_parser.add_argument(
            "--pr-count",
            type=self.parse_filter_count,
            default=-1,
            help="Minimum pull request count filter. Use -1 to disable.",
        )

        # Parse args
        return parser.parse_args()
