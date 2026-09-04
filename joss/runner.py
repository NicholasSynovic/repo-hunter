"""Coordinate extract-transform-load execution for JOSS data."""

from joss.db import DB
from joss.extract import JOSSExtract
from joss.load import JOSSLoad
from joss.logger import JOSSLogger
from joss.transform import JOSSTransform


class JOSSRunner:
    """Orchestrate the full JOSS ETL pipeline.

    Parameters
    ----------
    joss_logger : JOSSLogger
        Application logger wrapper.
    db : DB
        Target database connection and schema manager.
    resolve_urls : bool, default=False
        Whether to resolve JOSS paper URLs to their final redirect target.
    """

    def __init__(
        self,
        joss_logger: JOSSLogger,
        db: DB,
        resolve_urls: bool = False,
    ) -> None:
        """Create extractor, transformer, and loader components."""
        self.extract: JOSSExtract = JOSSExtract(joss_logger=joss_logger)
        self.transform: JOSSTransform = JOSSTransform(
            joss_logger=joss_logger,
            resolve_joss_url=resolve_urls,
        )
        self.load: JOSSLoad = JOSSLoad(joss_logger=joss_logger, db=db)

    def run(self) -> None:
        """Execute the JOSS ETL pipeline end-to-end."""
        data: list[dict] = self.extract.download_data()
        normalized_data: dict[str, list] = self.transform.transform_data(
            data=data,
        )
        self.load.load_data(data=normalized_data)
