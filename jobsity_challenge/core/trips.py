"""Trips module classes."""
import os
import logging
import logging.config
from pathlib import Path
from typing import Dict, List, Union, Optional

from pydantic import BaseModel

from jobsity_challenge.models import Table
from jobsity_challenge.constants import LOG_CONFIG
from jobsity_challenge.core.database import Database

logger = logging.getLogger(__name__)
logging.config.dictConfig(LOG_CONFIG)

# Load data from environments variables
DATABASE_CREDENTIALS = {
    "host": os.getenv("POSTGRES_HOST"),
    "engine_type": os.getenv("ENGINE_TYPE"),
    "port": os.getenv("POSTGRES_PORT"),
    "database": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}


class BaseJob(BaseModel):
    """Parent class with common methods and attributes."""

    pre_action: Optional[str]
    clean_action: Optional[str]
    action: str
    post_action: Optional[str]

    class Config:
        arbitrary_types_allowed = True

    def init_db(self, script_path: Path) -> None:
        """Create tables in database.

        Parameters
        ----------
        script_path : Path
            Path to `init_ddl.sql`
        """
        postgres = Database(**DATABASE_CREDENTIALS)
        postgres.execute_query(open(script_path, "r", encoding="utf-8").read())

    def run_pre_action(self) -> None:
        """Run query before the main action."""
        if self.pre_action:
            logger.info("Running pre_action")
            postgres = Database(**DATABASE_CREDENTIALS)
            # Input params to avoid sql injection
            postgres.execute_query(self.pre_action, {**self.__dict__})

    def run_action(self, full_load: bool) -> Union[str, None]:
        """Run main action.

        Parameters
        ----------
        full_load : bool
            If true truncate the table and then load, else only load the data

        Returns
        -------
        Union[str, None]
            Row count or None.
        """
        postgres = Database(**DATABASE_CREDENTIALS)

        if self.clean_action and full_load:
            action_query = self.clean_action + self.action
        else:
            action_query = self.action

        # Input params to avoid sql injection
        results = postgres.execute_query(action_query, {**self.__dict__})

        if results:
            row_count: str = results.__dict__.get("rowcount")
            return row_count
        else:
            return None

    def run_post_action(self) -> None:
        """Run action after main action."""
        if self.post_action:
            logger.info("Running post_action")
            postgres = Database(**DATABASE_CREDENTIALS)
            # Special case vacuum cannot run inside a block
            action_list = self.post_action.split(";")
            for action in action_list:
                if action.strip() != "":
                    # Input params to avoid sql injection
                    postgres.execute_query(action, {**self.__dict__})


class Ingestion(BaseJob, BaseModel):
    """Custom attributes for ingestion."""

    landing_file: str
    table_target: Table

    class Config:
        arbitrary_types_allowed = True


class Transform(BaseJob, BaseModel):
    """Custom attributes for transform."""

    table_source: Table
    table_target: Table

    class Config:
        arbitrary_types_allowed = True


class Report(BaseModel):
    """Class used for running queries."""

    query: str
    params: Dict

    class Config:
        arbitrary_types_allowed = True

    def get_report(self) -> Union[List, None]:
        """Execute query using class attributes.

        Returns
        -------
        Union[List, None]
            Query results
        """
        postgres = Database(**DATABASE_CREDENTIALS)
        results = postgres.execute_query(self.query, self.params)

        if results.cursor:
            return results.fetchall()  # type: ignore
        else:
            return None
