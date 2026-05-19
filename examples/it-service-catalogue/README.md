# IT Service Catalogue Example

Demonstrates adapting auto-search to a corporate IT helpdesk context. 53 items across 8 categories. Uses `examples/it-service-catalogue/config.yaml` with field names `service_id`, `category_id`, `title`, `summary`.

## Quick start

```bash
# Install the CLI + pipeline deps
pip install -e .
pip install -r fine-tuning/requirements.txt
pip install -r test-harness/requirements.txt

# Run the full pipeline (generate -> train -> export -> embed -> ui-config)
autosearch pipeline \
  --corpus examples/it-service-catalogue/corpus.json \
  --config examples/it-service-catalogue/config.yaml \
  --local

# Evaluate model quality
autosearch evaluate \
  --corpus examples/it-service-catalogue/corpus.json \
  --queries examples/it-service-catalogue/test-queries.json \
  --config examples/it-service-catalogue/config.yaml \
  --fine-tuned-model output/it-service-catalogue/model/
```

## Adapting to your own domain

1. Copy `examples/it-service-catalogue/config.yaml` (or `examples/health-workforce/config.yaml`) to a new folder for your project and customise.
2. Set `id_field`, `group_field`, `name_field`, `description_field` to match your corpus JSON keys.
3. Set `domain_description` to describe who will be searching (used to generate synthetic training queries).
4. Set `name` to a short identifier for your domain (used to namespace pipeline output).
5. Build your `corpus.json` — an array of objects with at least the four configured fields.
6. Run `autosearch pipeline --corpus your-corpus.json --config your-config.yaml --local`. **The `--config` flag is required** — without it the CLI defaults to the health-workforce config and applies the wrong field mappings to your corpus.
