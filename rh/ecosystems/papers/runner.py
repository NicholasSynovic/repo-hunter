"""Coordinate extract-transform-load execution for Papers data."""

from json import dump

from rh.db import DB
from rh.ecosystems.papers.extract import PapersExtract
from rh.ecosystems.papers.load import PapersLoad
from rh.ecosystems.papers.transform import PapersTransform
from rh.logger import JOSSLogger


class JOSSRunner:
    """Orchestrate the Ecosyste.ms Papers ETL pipeline.

    Parameters
    ----------
    joss_logger : JOSSLogger
        Application logger wrapper.
    db : DB
        Target database connection and schema manager.
    email : str
        Contact email supplied to the upstream API via ``mailto``.
    resolve_urls : bool, default=False
        Reserved option kept for CLI/API parity.
    """

    def __init__(
        self,
        joss_logger: JOSSLogger,
        db: DB,
        email: str,
        resolve_urls: bool = False,
    ) -> None:
        """Create extractor, transformer, and loader components."""
        self.extract: PapersExtract = PapersExtract(
            joss_logger=joss_logger,
            email=email,
        )
        self.transform: PapersTransform = PapersTransform(
            joss_logger=joss_logger,
        )
        self.load: PapersLoad = PapersLoad(joss_logger=joss_logger, db=db)

    def run(self) -> None:
        """Execute the Papers ETL pipeline end-to-end."""
        data: list[dict] = self.extract.download_data()
        normalized_data: dict[str, list] = self.transform.transform_data(
            data=data,
        )
        self.load.load_data(data=normalized_data)
