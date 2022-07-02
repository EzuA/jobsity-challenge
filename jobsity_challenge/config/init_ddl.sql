CREATE SCHEMA IF NOT EXISTS jobsity;

DROP TABLE IF EXISTS jobsity.trips;

CREATE TABLE jobsity.trips (
    region varchar(100),
    origin_coord geometry(Point, 4326),
    destination_coord geometry(Point, 4326),
    datetime timestamp,
    datasource varchar(200),
    _m_load_time timestamp NOT NULL DEFAULT NOW()
);

