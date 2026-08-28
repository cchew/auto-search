# Health Workforce Example

Reference domain for Auto Search: 350 synthetic health workforce planning items across 14 report groups (GP Workforce, Nursing Workforce, Allied Health, etc.). Fully self-contained — all config, corpus, and test data live in this folder.

## Quick start

```bash
# Install the CLI
pip install -e .

# Run the full pipeline (generate -> train -> export -> embed -> ui-config)
autosearch pipeline \
  --corpus examples/health-workforce/corpus.json \
  --config examples/health-workforce/config.yaml \
  --local

# Evaluate model quality
autosearch evaluate \
  --corpus examples/health-workforce/corpus.json \
  --queries examples/health-workforce/test-queries.json \
  --config examples/health-workforce/config.yaml \
  --fine-tuned-model output/health-workforce/model/
```

## Files

| File | Purpose |
|---|---|
| `corpus.json` | 350 health workforce items (synthetic). Shipped ready to use for local proof; `extract_corpus.sql` shows the query shape if you build one from a relational source. |
| `corpus-ui.json` | Frontend UI labels (title, lede, suggestions, group names) shipped with this example so the repo proves portability without re-running `autosearch ui-config`. |
| `config.yaml` | Field name mapping and pipeline settings for this domain (`item_id`, `wpp_id`, `name`, `description`). |
| `test-queries.json` | Evaluation queries for benchmarking model quality against this corpus. |
| `extract_corpus.sql` | Illustrative SQL showing the shape of query used to build `corpus.json` from a relational source. Export the result as a JSON array. |

## Adapting to your own domain

1. Copy `examples/health-workforce/config.yaml` (or `examples/it-service-catalogue/config.yaml`) to your project folder
2. Update `id_field`/`group_field`/`name_field`/`description_field` to match your JSON keys, set `name` and `pipeline.domain_description`
3. Supply your `corpus.json`
4. Run `autosearch pipeline --corpus your-corpus.json --config your-config.yaml --local`
5. Start the backend with `-D` flags pointing at your generated artefacts (see main [README](../../README.md#quick-start))
