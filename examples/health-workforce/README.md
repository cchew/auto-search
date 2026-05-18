# Health Workforce Example

This example uses the default `config.yaml` at repo root (field names: `item_id`, `wpp_id`, `name`, `description`).

`extract_corpus.sql` extracts a `corpus.json` from an Oracle database with the WPP schema. Run it in SQL Developer and export the result to `test-harness/data/corpus.json`.

The seed corpus in `test-harness/data/corpus.json` covers ~30 health workforce data items and can be used for a local proof run without database access.
