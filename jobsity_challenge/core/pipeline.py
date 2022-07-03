import logging
import logging.config
from typing import Dict
from pathlib import Path

import yaml

from jobsity_challenge.core.trips import Ingestion
from jobsity_challenge.models import ApiIngestConfig, IngestionConfig
from jobsity_challenge.constants import DDL_FILE, LOG_CONFIG, CONFIG_FILE

logger = logging.getLogger(__name__)
logging.config.dictConfig(LOG_CONFIG)

ROOT_DIR = Path(__file__).parent.parent.resolve()


def get_pipeline_config() -> Dict:
    with open(ROOT_DIR / CONFIG_FILE, "r", encoding="utf-8") as f:
        config: Dict = yaml.safe_load(f)
    return config


def ingest_data(ingest_config: ApiIngestConfig) -> None:
    config = get_pipeline_config()["ingestion"]

    ingestion_config = IngestionConfig(**config)
    ingestion = Ingestion(config=ingestion_config)

    logger.info("Loading data")
    if ingest_config.init_db:
        ingestion.init_db(ROOT_DIR / DDL_FILE)

    ingestion.pre_action()

    nro_rows = ingestion.load_data(ingest_config.full_load)
    logger.info(f"Number of rows loaded: {nro_rows}")

    ingestion.post_action()


if __name__ == "__main__":
    ingest_data(ApiIngestConfig(full_load=True, init_db=False))
