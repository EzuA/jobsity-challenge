import logging
import importlib
import logging.config
from pathlib import Path
from typing import Dict, List

import yaml

from jobsity_challenge.core.trips import Report
from jobsity_challenge.models import ApiInputConfig
from jobsity_challenge.constants import DDL_FILE, LOG_CONFIG, CONFIG_FILE

logger = logging.getLogger(__name__)
logging.config.dictConfig(LOG_CONFIG)

ROOT_DIR = Path(__file__).parent.parent.resolve()


def get_pipeline_config() -> Dict:
    with open(ROOT_DIR / CONFIG_FILE, "r", encoding="utf-8") as f:
        config: Dict = yaml.safe_load(f)
    return config


def ingest_data(api_input_config: ApiInputConfig) -> None:
    config = get_pipeline_config()["ingestion"]

    run_process(
        process_type="Ingestion",
        api_input_config=api_input_config,
        process_config=config,
    )


def transform_data(api_input_config: ApiInputConfig) -> None:
    tables = get_pipeline_config()["transform"]

    for config_table in tables:
        run_process(
            process_type="Transform",
            api_input_config=api_input_config,
            process_config=config_table,
        )


def run_process(
    process_type: str, api_input_config: ApiInputConfig, process_config: Dict
) -> None:
    module = importlib.import_module("jobsity_challenge.core.trips")
    process_class = getattr(module, process_type)
    process = process_class(**process_config)

    try:
        logger.info(f"Executing {process_type}")
        if api_input_config.init_db:
            process.init_db(ROOT_DIR / DDL_FILE)

        process.run_pre_action()

        nro_rows = process.run_action(api_input_config.full_load)
        logger.info(f"Number of rows affected: {nro_rows}")

        process.run_post_action()

    except Exception as e:
        raise e


def get_weekly_average(config_key: str, params: Dict) -> List[Dict]:
    config = get_pipeline_config()[config_key]

    logger.info(f"Calculating weekly average trips using: {params}")
    report = Report(**config, params=params)
    results = report.get_report()

    if results:
        return [{"AVG value": r[0]} for r in results]
    else:
        return [{"AVG value": ""}]


if __name__ == "__main__":
    # Testing run
    ingest_data(ApiInputConfig(full_load=False, init_db=True))
    transform_data(ApiInputConfig(full_load=False))
    print(
        get_weekly_average(
            config_key="weekly_average_report_region", params={"region": "Prague"}
        )
    )
