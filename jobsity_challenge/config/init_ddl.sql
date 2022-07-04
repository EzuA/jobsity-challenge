CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS dwh;

DROP TABLE IF EXISTS raw.trips;
CREATE TABLE raw.trips (
    region varchar,
    origin_coord geometry(Point, 4326),
    destination_coord geometry(Point, 4326),
    datetime timestamp,
    datasource varchar,
    _m_load_time timestamp NOT NULL DEFAULT NOW()
);
CREATE INDEX trips_region_str_idx2 ON raw.trips(region);
CREATE INDEX trips_datasource_str_idx2 ON raw.trips(datasource);

DROP TABLE IF EXISTS dwh.fact_trips;
CREATE TABLE dwh.fact_trips (
	region_id int NOT NULL,
	datasource_id int NOT NULL,
	year int NOT NULL,
	week int NOT NULL,
	origin_coord public.geometry(point, 4326) NOT NULL,
	destination_coord public.geometry(point, 4326) NOT NULL,
	"_m_created_at" timestamp NOT NULL DEFAULT now()
);
CREATE INDEX fact_trips_region_id_int_idx ON dwh.fact_trips USING btree (region_id);
CREATE INDEX fact_trips_datasource_id_int_idx ON dwh.fact_trips USING btree (datasource_id);
CREATE INDEX fact_trips_origin_geom_idx ON dwh.fact_trips USING gist (origin_coord);
CREATE INDEX fact_trips_destination_geom_idx ON dwh.fact_trips USING gist (destination_coord);

DROP TABLE IF EXISTS dwh.region;
CREATE TABLE dwh.region (
	id int NOT NULL GENERATED ALWAYS AS IDENTITY,
	region_name varchar NOT NULL,
	"_m_created_at" timestamp NOT NULL DEFAULT now()
);
CREATE INDEX region_id_str_idx ON dwh.region USING btree (region_name);

DROP TABLE IF EXISTS dwh.datasource;
CREATE TABLE dwh.datasource (
	id int NOT NULL GENERATED ALWAYS AS IDENTITY,
	datasource_name varchar NOT NULL,
	"_m_created_at" timestamp NOT NULL DEFAULT now()
);
CREATE INDEX datasource_id_str_idx ON dwh.datasource USING btree (datasource_name);
