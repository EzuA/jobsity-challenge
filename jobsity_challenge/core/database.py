import time
import logging
import logging.config
from typing import Any, Dict, Optional

from sqlalchemy.sql import text
from sqlalchemy import create_engine
from pydantic import Extra, BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import Engine, Result

from jobsity_challenge.constants import LOG_CONFIG

logger = logging.getLogger(__name__)
logging.config.dictConfig(LOG_CONFIG)


class Database(BaseModel):
    host: str
    port: int
    database: str
    user: str
    password: str
    engine_type: str
    engine: Engine = None

    class Config:
        arbitrary_types_allowed = True
        # Error on unknown attributes
        extra = Extra.forbid

    def __init__(self, **kwargs) -> None:  # type: ignore
        super().__init__(**kwargs)
        self.engine = self.get_engine()

    def get_engine(self) -> Engine:

        logger.info("Connecting to the database")

        conn_string = f"{self.engine_type}://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        engine = create_engine(
            conn_string,
            future=True,
            execution_options={"isolation_level": "AUTOCOMMIT"},
        )

        return engine

    def execute_query(
        self, query: str, query_params: Optional[Dict[str, Any]] = None
    ) -> Result:
        start = time.time()
        query_params = query_params or {}

        try:
            query = query.format(**query_params)
            logger.info(f"Executing: {query.strip()}")

            with self.engine.begin() as conn:
                results = conn.execute(text(query), query_params)
                end = time.time()
                logger.info(f"Elapsed time query: {round(end - start,2)}")
        except SQLAlchemyError as e:
            raise e

        return results
