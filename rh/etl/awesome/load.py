from loguru import logger
from pandas import DataFrame

from rh.db import DB
from rh.etl import LoadInterface
from rh.etl.awesome import AwesomeList, ListProject


class Load(LoadInterface):
    def __init__(self, db: DB) -> None:
        self.db: DB = db

    def load_data(
        self,
        lists: list[AwesomeList],
        projects: list[ListProject],
    ) -> None:
        logger.info(f"Writing data to {self.db._path}...")

        # Write Awesome lists to the `awesome_lists` table
        lists_table: DataFrame = DataFrame(data=[row.model_dump() for row in lists])
        lists_table.to_sql(
            name="awesome_lists",
            con=self.db.engine,
            if_exists="delete_rows",
            index=False,
        )
        logger.info(f"Wrote {len(lists)} lists to awesome_lists")

        # Write list projects to the `awesome_list_projects` table;
        # loaded second so the foreign key to `awesome_lists.id` is satisfied
        projects_table: DataFrame = DataFrame(
            data=[row.model_dump() for row in projects]
        )
        projects_table.to_sql(
            name="awesome_list_projects",
            con=self.db.engine,
            if_exists="delete_rows",
            index=False,
        )
        logger.info(f"Wrote {len(projects)} list projects to awesome_list_projects")

        logger.info(f"Wrote data to {self.db._path}")
