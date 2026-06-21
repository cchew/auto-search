FROM drupal:10-php8.3-apache

# Install intl (BertTokenizer uses IntlChar for Unicode normalisation) and
# FFI (required by ankane/onnxruntime-php to call libonnxruntime via libffi).
# libffi-dev is needed at build time for docker-php-ext-install ffi.
RUN apt-get update && \
    apt-get install -y --no-install-recommends libffi-dev libicu-dev default-mysql-client && \
    rm -rf /var/lib/apt/lists/* && \
    docker-php-ext-install ffi intl && \
    echo "ffi.enable=true" >> /usr/local/etc/php/php.ini

# Composer
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

# The Drupal project root is /opt/drupal (composer.json + vendor/).
# /var/www/html is a symlink to /opt/drupal/web (the document root).
# Install Drush and the ONNX PHP binding into the top-level project vendor/ so
# Drush can find drupal/core and the autosearch module can load onnxruntime.
# --ignore-platform-req=ext-ffi: ffi.enable is a runtime ini setting; Composer's
# static check sees the extension as absent at build time.
# Pin ankane/onnxruntime to the exact version tested against ONNX Runtime 1.26.0.
# A version bump could change the expected .so path and break the FFI load silently.
COPY composer.lock /opt/drupal/composer.lock
RUN composer require "drush/drush:^13" "ankane/onnxruntime:0.3.3" \
    --working-dir=/opt/drupal \
    --ignore-platform-req=ext-ffi \
    --no-interaction \
    --no-progress

# ankane/onnxruntime v0.3.3 expects ONNX Runtime 1.26.0 and downloads it via a
# post-install Composer hook that is skipped with --no-interaction.
# Download it explicitly so the .so is baked into the image.
RUN php -r "require '/opt/drupal/vendor/autoload.php'; OnnxRuntime\Vendor::check();"

# Auto-install entrypoint
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
