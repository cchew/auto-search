# Health Workforce Example

Reference domain for Auto Search: 350 synthetic health workforce planning items across 14 report groups (GP Workforce, Nursing Workforce, Allied Health, etc.). Uses the default `config.yaml` at repo root (field names: `item_id`, `wpp_id`, `name`, `description`).

## Quick start

```bash
# Install the CLI
pip install -e .

# Run the full pipeline (generate -> train -> export -> embed -> ui-config)
autosearch pipeline \
  --corpus examples/health-workforce/corpus.json \
  --config config.yaml \
  --local

# Evaluate model quality
autosearch evaluate \
  --corpus examples/health-workforce/corpus.json \
  --queries test-harness/data/test-queries.json \
  --config config.yaml \
  --fine-tuned-model output/health-workforce/model/
```

## Files

| File | Purpose |
|---|---|
| `corpus.json` | 350 health workforce items (synthetic). Generated from `extract_corpus.sql` for a real DHDA run, or used as-is for local proof. |
| `corpus-ui.json` | Frontend UI labels (title, lede, suggestions, group names) shipped with this example so the repo proves portability without re-running `autosearch ui-config`. |
| `extract_corpus.sql` | Oracle SQL to extract a fresh `corpus.json` from the Workforce Planning Reports schema. Run in SQL Developer; export result as `corpus.json` (JSON Array format). |

## Adapting to your own domain

See [examples/it-service-catalogue/README.md](../it-service-catalogue/README.md) for a fully self-contained example with its own `config.yaml`. The general steps are:

1. Copy `config.yaml` (repo root) to your project, update `id_field`/`group_field`/`name_field`/`description_field` to match your JSON keys, set `name` and `pipeline.domain_description`
2. Supply your `corpus.json`
3. Run `autosearch pipeline --corpus your-corpus.json --config your-config.yaml --local`
4. Start the backend with `-D` flags pointing at your generated artefacts (see main [README](../../README.md#quick-start))
