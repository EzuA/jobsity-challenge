WITH two_regions AS (
    SELECT
        region,
        count(*)
    FROM
        raw.trips
    GROUP BY
        region
    ORDER BY
        count(*) DESC
    LIMIT
        2
), latest AS (
    SELECT
        t.region,
        max(datetime) AS latest_datetime
    FROM
        raw.trips AS t
        INNER JOIN two_regions AS r ON t.region = r.region
    GROUP BY
        t.region
)
SELECT
    t.region,
    datasource
FROM
    raw.trips AS t
    INNER JOIN latest AS l ON t.datetime = l.latest_datetime
