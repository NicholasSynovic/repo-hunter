"""CLI argument helpers for the standalone JOSS command."""

# Copyright (c) 2025 Nicholas M. Synovic

import os
from argparse import ArgumentParser, Namespace
from pathlib import Path

APPLICATION_NAME: str = "joss"


class CLI:
    """Build the argument parser for the JOSS sub-command."""

    @staticmethod
    def add_out_file_argument(
        parser: ArgumentParser,
        *,
        required: bool = True,
    ) -> None:
        """Add the ``--out-file`` argument to a parser.

        Parameters
        ----------
        parser : ArgumentParser
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
    def add_resolve_urls_flag(
        parser: ArgumentParser,
        *,
        required: bool = False,
    ) -> None:
        """Add the ``--resolve-urls`` argument to a parser.

        Parameters
        ----------
        parser : ArgumentParser
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
        """Read ``GITHUB_TOKEN`` from the environment.

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

    def run(self, argv: list[str] | None = None) -> Namespace:
        """Build and run the CLI argument parser.

        Parameters
        ----------
        argv : list[str] | None, default=None
            Optional argument list to parse. If ``None``, parse ``sys.argv``.

        Returns
        -------
        Namespace
            Parsed command-line arguments.

        """
        args: Namespace = self.build_parser().parse_args(argv)
        return args

    def build_parser(self) -> ArgumentParser:
        """Build the CLI argument parser.

        Returns
        -------
        ArgumentParser
            Configured parser instance.

        """
        parser = ArgumentParser(
            prog=APPLICATION_NAME,
            description=f"{APPLICATION_NAME} dataset toolkit.",
        )

        self._add_joss_parser(parser=parser)

        return parser

    def _add_joss_parser(self, parser: ArgumentParser) -> None:
        """Register the JOSS arguments on the CLI parser.

        Parameters
        ----------
        parser : ArgumentParser
            Argument parser to augment.

        """
        self.add_out_file_argument(parser=parser, required=True)
        self.add_resolve_urls_flag(parser=parser, required=False)
