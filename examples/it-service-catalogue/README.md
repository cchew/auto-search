# IT Service Catalogue Example

Demonstrates adapting auto-search to a corporate IT helpdesk context. Uses `examples/it-service-catalogue/config.yaml` with field names `service_id`, `category_id`, `title`, `summary`.

## Quick start

```bash
# Install the CLI
pip install -e .

# Run the full pipeline using the IT service catalogue corpus
autosearch pipeline \
  --corpus examples/it-service-catalogue/corpus.json \
  --config examples/it-service-catalogue/config.yaml \
  --local

# Evaluate model quality
autosearch evaluate \
  --corpus examples/it-service-catalogue/corpus.json \
  --queries examples/it-service-catalogue/test-queries.json \
  --config examples/it-service-catalogue/config.yaml
```

## Adapting to your own domain

1. Copy `examples/it-service-catalogue/config.yaml` to your project root as `config.yaml`
2. Set `id_field`, `group_field`, `name_field`, `description_field` to match your corpus JSON keys
3. Set `domain_description` to describe who will be searching (used to generate synthetic training queries)
4. Set `name` to a short identifier for your domain (used to namespace pipeline output)
5. Build your `corpus.json` -- an array of objects with at least the four configured fields
6. Run `autosearch pipeline --corpus your-corpus.json --local`
