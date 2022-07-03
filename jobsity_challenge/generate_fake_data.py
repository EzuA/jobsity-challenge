import os
import csv
import time
import multiprocessing
from typing import Dict
from datetime import datetime

import numpy as np
from faker import Faker

fake = Faker()
PATH_DATA = "raw_data/fake"
ROWS_PER_FILE = 12500000
NUM_FILES = 8


def generate_trip(seed: int) -> Dict:

    datasource_list = [
        "bad_diesel_vehicles",
        "cheap_mobile",
        "pt_search_app",
        "funny_car",
        "baba_car",
    ]
    countries = ["CZ", "DE", "IT"]

    np.random.seed(seed)
    country = np.random.choice(countries)
    place_1 = fake.local_latlng(country)
    place_2 = fake.local_latlng(country)

    return {
        "region": place_1[4].split("/")[1],
        "origin_coord": f"POINT ({place_1[1]} {place_1[0]})",
        "destination_coord": f"POINT ({place_2[1]} {place_2[0]})",
        "datetime": fake.date_time_between(start_date="-5y"),
        "datasource": np.random.choice(datasource_list),
    }


def generate_csv(file_name: str) -> None:
    with open(file_name, "w", encoding="utf-8") as file:
        columns = [
            "region",
            "origin_coord",
            "destination_coord",
            "datetime",
            "datasource",
        ]

        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        for _ in range(ROWS_PER_FILE):
            seed = file_name.split("-")[1].split(".")[0]
            writer.writerow(generate_trip(int(seed)))


if __name__ == "__main__":
    start = time.time()
    print(f"Start: {datetime.now()}")

    os.makedirs(PATH_DATA, exist_ok=True)
    file_list = [f"{PATH_DATA}/trips-{i}.csv" for i in range(NUM_FILES)]
    pool = multiprocessing.Pool()
    pool.map(generate_csv, file_list)

    end = time.time()
    print(f"Elapsed time: {round(end - start,2)}")
