SELECT
    region
FROM
    raw.trips t
WHERE
    t.datasource = 'cheap_mobile'
GROUP BY
    region
