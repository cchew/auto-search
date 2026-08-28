-- Illustrative query showing the shape of source data that corpus.json is built from.
-- Run against your own relational source; export the result as a JSON array.
SELECT
    di.item_id,
    grp.wpp_id,
    di.item_name                 AS name,
    NVL(di.item_description, '')  AS description
FROM
    catalogue_items di
    JOIN item_groups grp ON di.wpp_id = grp.wpp_id
WHERE
    di.active_flag = 'Y'
ORDER BY
    grp.wpp_id, di.item_id;
