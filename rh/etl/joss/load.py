from loguru import logger
from pandas import DataFrame

from rh.db import DB
from rh.etl import LoadInterface
from rh.etl.joss import JOSSGHIssue, JOSSPaperProjectIssue


class Load(LoadInterface):
    def __init__(self, db: DB) -> None:
        self.db: DB = db

    def load_data(
        self,
        issues: list[JOSSGHIssue],
        ppi: list[JOSSPaperProjectIssue],
    ) -> None:
        logger.info(f"Writing data to {self.db._path}...")

        # Write GitHub issues to the `joss_github_issues` table
        issues_table: DataFrame = DataFrame(data=[i.model_dump() for i in issues])
        issues_table.to_sql(
            name="joss_github_issues",
            con=self.db.engine,
            if_exists="delete_rows",
            index=False,
        )
        logger.info(f"Wrote {len(issues)} issues to joss_github_issues")

        # Write paper project issues to the `joss_paper_project_issues` table;
        # loaded second so the foreign key to `joss_github_issues.id` is satisfied
        ppi_table: DataFrame = DataFrame(data=[i.model_dump() for i in ppi])
        ppi_table.to_sql(
            name="joss_paper_project_issues",
            con=self.db.engine,
            if_exists="delete_rows",
            index=False,
        )
        logger.info(
            f"Wrote {len(ppi)} paper project issues to joss_paper_project_issues"
        )

        logger.info(f"Wrote data to {self.db._path}")
