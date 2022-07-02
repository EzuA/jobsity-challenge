import os
import logging
import logging.config
from typing import Union

from pydantic import BaseModel

from jobsity_challenge.constants import LOG_CONFIG
from jobsity_challenge.core.database import Database
from jobsity_challenge.models import IngestionConfig

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


class Ingestion(BaseModel):
    config: IngestionConfig

    class Config:
        arbitrary_types_allowed = True

    def init_db(self, script_path: str) -> None:
        postgres = Database(**DATABASE_CREDENTIALS)
        postgres.execute_query(open(script_path, "r", encoding="utf-8").read())

    def load_data(self, full_load: bool) -> Union[str, None]:
        postgres = Database(**DATABASE_CREDENTIALS)
        query = (self.config.pre_action if full_load else "") + self.config.action
        results = postgres.execute_query(query, {**self.config.__dict__})

        if results:
            row_count: str = results.__dict__.get("rowcount")
            return row_count
        else:
            return None
