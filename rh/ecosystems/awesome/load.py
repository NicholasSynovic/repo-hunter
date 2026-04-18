"""Load transformed Awesome records into SQLite tables."""

from logging import Logger

from pandas import DataFrame
from progress.bar import Bar

from rh.db import DB
from rh.interfaces import LoadInterface
from rh.logger import JOSSLogger


class PapersLoad(LoadInterface):
    """Loader for Ecosyste.ms Awesome table payloads.

    Parameters
    ----------
    joss_logger : JOSSLogger
        Application logger wrapper.
    db : DB
        Database wrapper containing SQLAlchemy engine and metadata.
    """

    def __init__(self, joss_logger: JOSSLogger, db: DB) -> None:
        """Initialize the loader with logger and target database."""
        self.db: DB = db
        self.logger: Logger = joss_logger.get_logger()

    def load_data(self, data: dict[str, list]) -> bool:
        """Write transformed records to destination tables.

        Parameters
        ----------
        data : dict[str, list]
            Mapping of table names to row dictionaries.

        Returns
        -------
        bool
            ``True`` when all table writes complete.
        """
        table_names: list[str] = list(data.keys())

        self.logger.info("Writing data to `%s`", self.db._path)
        with Bar(
            f"Writing data to `{self.db._path}`... ",
            max=len(table_names),
        ) as bar:
            table: str
            for table in table_names:
                content: DataFrame = DataFrame(data=data[table])
                content.to_sql(
                    name=table,
                    con=self.db.engine,
                    if_exists="delete_rows",
                    index=False,
                    index_label="_id",
                )
                self.logger.info("Wrote data to `%s`", table)
                bar.next()

        return True
