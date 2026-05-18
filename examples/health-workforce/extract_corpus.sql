-- Run against a relational source Oracle schema.
-- Export result as corpus.json (JSON Array format).
SELECT
    di.item_id,
    wpp.wpp_id,
    di.item_name   AS name,
    NVL(di.item_description, '') AS description
FROM
    data_items di
    JOIN item_groups wpp ON di.wpp_id = wpp.wpp_id
WHERE
    di.active_flag = 'Y'
ORDER BY
    wpp.wpp_id, di.item_id;
