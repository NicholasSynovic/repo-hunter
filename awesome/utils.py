"""Utility functions for the Awesome dataset toolkit."""

from __future__ import annotations

from datetime import UTC, datetime


class Utils:
    """Utility methods for timestamp handling."""

    @staticmethod
    def get_timestamp() -> int:
        """
        Return the current UTC time in ISO-8601 format (seconds precision).

        Returns
        -------
        int
            Current UTC timestamp in Unix seconds.

        """
        return int(
            datetime.now(tz=UTC)
            .replace(
                microsecond=0,
            )
            .timestamp()
        )
