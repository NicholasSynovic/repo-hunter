from json import dump

from rh.db import DB
from rh.ecosystems.papers.extract import PapersExtract
from rh.ecosystems.papers.transform import PapersTransform
from rh.ecosystems.papers.load import PapersLoad
from rh.logger import JOSSLogger


class JOSSRunner:
    def __init__(
        self,
        joss_logger: JOSSLogger,
        db: DB,
        email: str,
        resolve_urls: bool = False,
    ) -> None:
        self.extract: PapersExtract = PapersExtract(
            joss_logger=joss_logger,
            email=email,
        )
        self.transform: PapersTransform = PapersTransform(
            joss_logger=joss_logger,
        )
        self.load: PapersLoad = PapersLoad(joss_logger=joss_logger, db=db)

    def run(self) -> None:
        data: list[dict] = self.extract.download_data()
        normalized_data: dict[str, list] = self.transform.transform_data(
            data=data,
        )
        self.load.load_data(data=normalized_data)
