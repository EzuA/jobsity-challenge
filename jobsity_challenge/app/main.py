import time
import hashlib
import logging
import logging.config
from typing import Any, Dict

from fastapi import Depends, FastAPI, HTTPException, BackgroundTasks

from jobsity_challenge.constants import LOG_CONFIG
from jobsity_challenge.models import ApiInputConfig, ApiInputBoundingBox
from jobsity_challenge.core.pipeline import (
    init_db,
    run_all,
    ingest_data,
    transform_data,
    get_weekly_average,
)

logger = logging.getLogger(__name__)
logging.config.dictConfig(LOG_CONFIG)

app = FastAPI(title="jobsity challenge API")


def run_process(
    process_config: ApiInputConfig,
    background_tasks: BackgroundTasks,
    process_function: Any,
    process_type: str,
) -> Dict[str, Any]:
    process_id = hashlib.md5(str(time.time()).encode("utf-8")).hexdigest()
    try:
        background_tasks.add_task(process_function, process_config, process_id)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=404, detail=str(e)) from e
    else:
        return {"status": f"Data {process_type} started", "process_id": process_id}


@app.get("/", tags=["Welcome message"])
async def root() -> Dict:
    return {"message": "Welcome to jobsity challenge API"}


@app.post("/init_db/", status_code=201, tags=["Data pipeline process"])
async def init() -> Dict[str, Any]:
    try:
        init_db()
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=404, detail=str(e)) from e
    else:
        return {"status": "Database tables created"}


@app.post("/ingest/", status_code=201, tags=["Data pipeline process"])
async def ingest(
    process_config: ApiInputConfig, background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    return run_process(
        process_config,
        background_tasks,
        process_function=ingest_data,
        process_type="ingestion",
    )


@app.post("/transform/", status_code=201, tags=["Data pipeline process"])
async def transform(
    process_config: ApiInputConfig, background_tasks: BackgroundTasks
) -> Dict:
    return run_process(
        process_config,
        background_tasks,
        process_function=transform_data,
        process_type="transform",
    )


@app.post("/run_all/", status_code=201, tags=["Data pipeline process"])
async def run_all_processes(
    process_config: ApiInputConfig, background_tasks: BackgroundTasks
) -> Dict:
    return run_process(
        process_config,
        background_tasks,
        process_function=run_all,
        process_type="ingestion & transform",
    )


@app.get("/weekly_average_region", status_code=200, tags=["Execute querys"])
async def weekly_average_region(region: str) -> Dict:

    try:
        results = get_weekly_average(
            config_key="weekly_average_report_region", params={"region": region}
        )

    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=404, detail=str(e)) from e
    else:
        return {"data": results}


@app.get("/weekly_average_bounding_box/", status_code=200, tags=["Execute querys"])
async def weekly_average_bounding_box(
    bounding_box: ApiInputBoundingBox = Depends(ApiInputBoundingBox),
) -> Dict:
    try:
        results = get_weekly_average(
            config_key="weekly_average_report_bounding_box",
            params=bounding_box.__dict__,
        )
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=404, detail=str(e)) from e
    else:
        return {"data": results}
