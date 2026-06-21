#!/usr/bin/env bash
# Copy model artefacts from the Java build output into the Drupal module.
# Run once after training a new model, then rebuild the Docker image.
#
# Usage: bash setup-model.sh <corpus>
#   corpus: it-service-catalogue (default) | health-workforce
#
set -euo pipefail

CORPUS="${1:-it-service-catalogue}"
REPO_OUTPUT="../output/${CORPUS}/artefacts"
EXAMPLES="../examples/${CORPUS}"
DEST="modules/autosearch/model"

mkdir -p "$DEST"

echo "Copying model artefacts from $REPO_OUTPUT"
cp "${REPO_OUTPUT}/autosearch-embed.onnx"  "$DEST/autosearch-embed.onnx"
cp "${REPO_OUTPUT}/vocab.txt"              "$DEST/vocab.txt"
cp "${REPO_OUTPUT}/tokenizer.json"         "$DEST/tokenizer.json"

echo "Copying corpus data from $EXAMPLES"
cp "${EXAMPLES}/corpus.json"               "$DEST/corpus.json"
cp "${EXAMPLES}/corpus-ui.json"            "$DEST/ui-config.json"

# The pre-computed embeddings live in data-items.json (includes embedding field).
cp "../output/${CORPUS}/data-items.json" "$DEST/embeddings.json"

echo ""
echo "Model files in $DEST:"
ls -lh "$DEST"
echo ""
echo "Next: docker compose up --build"
