from joss.db import DB
from joss.ecosystems.papers.extract import PaperExtractor
from joss.joss.load import JOSSLoad
from joss.joss.transform import JOSSTransform
from joss.logger import JOSSLogger
from json import dump


class JOSSRunner:
    def __init__(
        self,
        joss_logger: JOSSLogger,
        db: DB,
        email: str,
        resolve_urls: bool = False,
    ) -> None:
        self.extract: PaperExtractor = PaperExtractor(joss_logger=joss_logger, email=email,)
        # self.transform: JOSSTransform = JOSSTransform(
        #     joss_logger=joss_logger,
        #     resolve_joss_url=resolve_urls,
        # )
        # self.load: JOSSLoad = JOSSLoad(joss_logger=joss_logger, db=db)

    def run(self) -> None:
        data: list[dict] = self.extract.download_data()
        with open("test.json", mode="w") as fp:
            dump(obj=data, fp=fp, indent=4)
        # normalized_data: dict[str, list] = self.transform.transform_data(
        #     data=data,
        # )
        # self.load.load_data(data=normalized_data)
