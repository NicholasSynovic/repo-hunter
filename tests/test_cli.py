"""Tests for CLI parser behavior and gh filter normalization."""

from __future__ import annotations

import argparse

import pytest

from rh.cli import CLI


def test_run_requires_subparser() -> None:
    """CLI should require a subcommand."""
    with pytest.raises(SystemExit):
        CLI().run(argv=[])


def test_gh_defaults_normalize_to_none() -> None:
    """Disabled gh filter sentinel values should normalize to ``None``."""
    args = CLI().run(argv=["gh"])

    assert args.dataset == "gh"
    assert args.star_count is None
    assert args.fork_count is None
    assert args.watcher_count is None
    assert args.issue_count is None
    assert args.age_months is None
    assert args.pr_count is None


def test_gh_explicit_values_preserved() -> None:
    """Provided gh thresholds should remain integers."""
    args = CLI().run(
        argv=[
            "gh",
            "--star-count",
            "100",
            "--fork-count",
            "20",
            "--watcher-count",
            "5",
            "--issue-count",
            "7",
            "--age-months",
            "12",
            "--pr-count",
            "3",
        ],
    )

    assert args.star_count == 100
    assert args.fork_count == 20
    assert args.watcher_count == 5
    assert args.issue_count == 7
    assert args.age_months == 12
    assert args.pr_count == 3


def test_filter_parser_rejects_below_disabled_sentinel() -> None:
    """Filter parser should reject values lower than ``-1``."""
    with pytest.raises(argparse.ArgumentTypeError):
        CLI.parse_filter_count("-2")


def test_filter_parser_rejects_non_integer() -> None:
    """Filter parser should reject non-integer strings."""
    with pytest.raises(argparse.ArgumentTypeError):
        CLI.parse_filter_count("abc")


def test_existing_subcommands_still_parse() -> None:
    """Existing dataset subcommands should continue to parse correctly."""
    joss_args = CLI().run(argv=["joss", "--out-file", "/tmp/joss.db"])
    papers_args = CLI().run(
        argv=["papers", "--out-file", "/tmp/papers.db", "--email", "you@example.com"],
    )
    awesome_args = CLI().run(
        argv=["awesome", "--out-file", "/tmp/awesome.db", "--email", "you@example.com"],
    )

    assert joss_args.dataset == "joss"
    assert papers_args.dataset == "papers"
    assert awesome_args.dataset == "awesome"
