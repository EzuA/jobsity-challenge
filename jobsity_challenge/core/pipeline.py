"""Pipeline runner module."""
import os
import logging
import importlib
import logging.config
from pathlib import Path
from typing import Dict, List

import yaml

from jobsity_challenge.models import ApiInputConfig
from jobsity_challenge.core.trips import Report, BaseJob
from jobsity_challenge.core.slack import slack_send_alert
from jobsity_challenge.constants import DDL_FILE, LOG_CONFIG, CONFIG_FILE

logger = logging.getLogger(__name__)
logging.config.dictConfig(LOG_CONFIG)

ROOT_DIR = Path(__file__).parent.parent.resolve()
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def get_pipeline_config() -> Dict:
    with open(ROOT_DIR / CONFIG_FILE, "r", encoding="utf-8") as f:
        config: Dict = yaml.safe_load(f)
    return config


def init_db() -> None:
    """Initialize the database."""
    job = BaseJob(action="Init database")

    # jobsity_challenge/config/init_ddl.sql
    job.init_db(script_path=ROOT_DIR / DDL_FILE)


def ingest_data(api_input_config: ApiInputConfig, process_id: str) -> None:
    """Ingest the data to the database.

    Parameters
    ----------
    api_input_config : ApiInputConfig
        Input parameters class
    process_id : str
        Hash that identifies a specific run
    """
    config = get_pipeline_config()["ingestion"]

    run_process(
        process_type="Ingestion",
        api_input_config=api_input_config,
        process_config=config,
        process_id=process_id,
    )


def transform_data(api_input_config: ApiInputConfig, process_id: str) -> None:
    """Run transformation queries.

    Parameters
    ----------
    api_input_config : ApiInputConfig
        Input parameters class
    process_id : str
        Hash that identifies a specific run
    """
    tables = get_pipeline_config()["transform"]

    for config_table in tables:
        run_process(
            process_type="Transform",
            api_input_config=api_input_config,
            process_config=config_table,
            process_id=process_id,
        )


def run_all(api_input_config: ApiInputConfig, process_id: str) -> None:
    """Run all process.

    Parameters
    ----------
    api_input_config : ApiInputConfig
        Input parameters class
    process_id : str
        Hash that identifies a specific run
    """
    init_db()
    ingest_data(api_input_config, process_id)
    transform_data(api_input_config, process_id)


def run_process(
    process_type: str,
    api_input_config: ApiInputConfig,
    process_config: Dict,
    process_id: str,
) -> None:
    """Execute a generic function used by ingestion & transform methods.

    Parameters
    ----------
    process_type : str
        Class type name. For example: Ingestion or Transform.
    api_input_config : ApiInputConfig
        Input parameters class
    process_config : Dict
        _description_
    process_id : str
        Hash that identifies a specific run
    """
    # Dynamic class import
    module = importlib.import_module("jobsity_challenge.core.trips")
    process_class = getattr(module, process_type)
    process = process_class(**process_config)

    try:
        logger.info(f"Executing {process_type}")
        if api_input_config.init_db:
            process.init_db(ROOT_DIR / DDL_FILE)

        # Run query before the main action
        process.run_pre_action()

        nro_rows = process.run_action(api_input_config.full_load)
        logger.info(f"Number of rows affected: {nro_rows}")

        # Run post query process, usually VACUUM ANALIZE
        process.run_post_action()

    except Exception as e:
        if SLACK_WEBHOOK_URL:
            slack_send_alert(
                webhook_url=SLACK_WEBHOOK_URL,
                title=f"Jobsity - Trips {process_type.lower()}",
                message=f"*Process ID*: {process_id}\n\n*Status*: Error processing {process_type.lower()}: {str(e)}",
                icon_emoji=":red_circle:",
            )
        raise e
    else:
        if SLACK_WEBHOOK_URL and process_type == "Ingestion":
            # We are interested in ingestion process success, not in every process
            slack_send_alert(
                webhook_url=SLACK_WEBHOOK_URL,
                title=f"Jobsity - Trips {process_type.lower()}",
                message=f"*Process ID*: {process_id}\n\n*Status*: {process_type.lower()} executed succesfully",
                icon_emoji=":white_check_mark:",
            )


def get_weekly_average(config_key: str, params: Dict) -> List[Dict]:
    """Get weekly average number of trips using params for filtering.

    Parameters
    ----------
    config_key : str
        Key name of the yaml config file. For example: ingestion, transform
    params : Dict
        Query params

    Returns
    -------
    List[Dict]
        Query results
    """
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
    run_all(ApiInputConfig(full_load=True), process_id="Reset database and data")
    print(
        get_weekly_average(
            config_key="weekly_average_report_region", params={"region": "Prague"}
        )
    )
