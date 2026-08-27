#!/usr/bin/env bash
# Copy model artefacts from the Java build output into the Drupal module.
# If you haven't run the training pipeline yourself, downloads a pretrained
# copy from the repo's GitHub Release instead (fresh-clone / demo path).
#
# Usage: bash setup-model.sh <corpus>
#   corpus: it-service-catalogue (default) | health-workforce
#
set -euo pipefail

CORPUS="${1:-it-service-catalogue}"
REPO_OUTPUT="../output/${CORPUS}/artefacts"
EXAMPLES="../examples/${CORPUS}"
DEST="modules/autosearch/model"
RELEASE_TAG="drupal-demo-assets-v1"
RELEASE_URL="https://github.com/cchew/auto-search/releases/download/${RELEASE_TAG}/autosearch-model-${CORPUS}.tar.gz"

mkdir -p "$DEST"

if [ ! -f "${REPO_OUTPUT}/autosearch-embed.onnx" ]; then
  echo "No local ../output/${CORPUS} found (expected on a fresh clone, output/ is gitignored)."
  echo "Downloading pretrained model + embeddings for '${CORPUS}' from the GitHub Release..."
  TMP_DOWNLOAD="$(mktemp -d)"
  curl -fL "$RELEASE_URL" -o "$TMP_DOWNLOAD/model.tar.gz"
  mkdir -p ../output
  tar -xzf "$TMP_DOWNLOAD/model.tar.gz" -C ../output
  rm -rf "$TMP_DOWNLOAD"
  echo "Downloaded to ../output/${CORPUS}/"
fi

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
