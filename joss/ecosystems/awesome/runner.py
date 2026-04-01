from json import dump

from joss.db import DB
from joss.ecosystems.awesome.extract import AwesomeExtract

# from joss.ecosystems.papers.load import PapersLoad
# from joss.ecosystems.papers.transform import PapersTransform
from joss.logger import JOSSLogger


class JOSSRunner:
    def __init__(
        self,
        joss_logger: JOSSLogger,
        db: DB,
        email: str,
        resolve_urls: bool = False,
    ) -> None:
        self.extract: AwesomeExtract = AwesomeExtract(
            joss_logger=joss_logger,
            email=email,
        )
        # self.transform: PapersTransform = PapersTransform(
        #     joss_logger=joss_logger,
        # )
        # self.load: PapersLoad = PapersLoad(joss_logger=joss_logger, db=db)

    def run(self) -> None:
        data: list[dict] = self.extract.download_data()
        from pprint import pprint as print

        print(data)

        # normalized_data: dict[str, list] = self.transform.transform_data(
        #     data=data,
        # )
        # self.load.load_data(data=normalized_data)
