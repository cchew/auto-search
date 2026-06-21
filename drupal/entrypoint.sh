#!/usr/bin/env bash
# Entrypoint for the autosearch Drupal demo container.
# On first run, waits for the DB and installs Drupal automatically.
# On subsequent runs, skips installation and starts Apache directly.
set -euo pipefail

# /var/www/html is a symlink to /opt/drupal/web (the document root).
# The composer project root (with vendor/ and drush) is /opt/drupal.
DRUPAL_PROJECT=/opt/drupal
DRUPAL_WEB=$DRUPAL_PROJECT/web
DRUSH=$DRUPAL_PROJECT/vendor/bin/drush
SETTINGS=$DRUPAL_WEB/sites/default/settings.php

echo "[entrypoint] Verifying model files..."
MODEL_DIR="$DRUPAL_WEB/modules/custom/autosearch/model"
for f in autosearch-embed.onnx vocab.txt corpus.json embeddings.json ui-config.json; do
  if [[ ! -f "$MODEL_DIR/$f" ]]; then
    echo "[entrypoint] ERROR: model file missing: $f"
    echo "[entrypoint]   Run: bash setup-model.sh health-workforce  (from drupal/)"
    exit 1
  fi
done
echo "[entrypoint] Model files OK."

echo "[entrypoint] Waiting for database..."
until mysqladmin ping -h db -u drupal -pdrupal --skip-ssl --silent 2>/dev/null; do
  sleep 2
done
echo "[entrypoint] Database ready."

drupal_installed() {
  [[ -f "$SETTINGS" ]] && \
  cd "$DRUPAL_WEB" && "$DRUSH" status --field=db-status 2>/dev/null | grep -q "Connected"
}

if ! drupal_installed; then
  echo "[entrypoint] First run — installing Drupal..."

  if [[ ! -f "$SETTINGS" ]]; then
    cp "$DRUPAL_WEB/sites/default/default.settings.php" "$SETTINGS"
  fi
  chmod 666 "$SETTINGS"
  chown www-data:www-data "$SETTINGS"

  cd "$DRUPAL_WEB"
  "$DRUSH" site:install minimal \
    --db-url=mysql://drupal:drupal@db/drupal \
    --account-name=admin \
    --account-pass=admin \
    --site-name="Auto Search" \
    --yes

  echo "[entrypoint] Generating lazy-service proxy classes..."
  for class in BertTokenizer EmbeddingService SimilarityService; do
    php core/scripts/generate-proxy-class.php \
      "Drupal\\autosearch\\${class}" \
      "modules/custom/autosearch/src" 2>/dev/null || true
  done

  echo "[entrypoint] Enabling autosearch module..."
  "$DRUSH" en autosearch --yes

  echo "[entrypoint] Clearing caches..."
  "$DRUSH" cr

  echo "[entrypoint] Done. Visit http://localhost:8080/autosearch"
else
  echo "[entrypoint] Already installed — skipping setup."
fi

echo "[entrypoint] Validating ONNX model..."
php -r "
require '/opt/drupal/vendor/autoload.php';
\$path = '$MODEL_DIR/autosearch-embed.onnx';
new OnnxRuntime\InferenceSession(\$path);
echo '[entrypoint] ONNX model OK' . PHP_EOL;
" || { echo "[entrypoint] ERROR: ONNX model failed to load — check FFI and libonnxruntime"; exit 1; }

echo "[entrypoint] Starting Apache..."
echo "[entrypoint] TIP: pre-load the ONNX model before demo:"
echo "[entrypoint]   curl -s -X POST http://localhost:8080/api/v1/search -H 'Content-Type: application/json' -d '{\"query\":\"health workforce\",\"topK\":1}'"
exec apache2-foreground
