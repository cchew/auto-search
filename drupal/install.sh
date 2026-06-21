#!/usr/bin/env bash
# One-time setup after "docker compose up --build".
# Enables the autosearch module once Drupal has been installed via the web wizard.
#
# Steps:
#   1. docker compose up --build
#   2. Open http://localhost:8080 — run the web installer (MySQL / db / drupal / drupal)
#   3. bash install.sh
#   4. Visit http://localhost:8080/autosearch
set -euo pipefail

CONTAINER=drupal-drupal-1
ENABLE_MODULE_PHP='<?php
define("DRUPAL_ROOT", "/var/www/html");
chdir(DRUPAL_ROOT);
$_SERVER["HTTP_HOST"] = "localhost";
$_SERVER["REMOTE_ADDR"] = "127.0.0.1";
$_SERVER["REQUEST_URI"] = "/";
$_SERVER["REQUEST_METHOD"] = "GET";
$autoloader = require DRUPAL_ROOT . "/autoload.php";
$kernel = \Drupal\Core\DrupalKernel::createFromRequest(
  \Symfony\Component\HttpFoundation\Request::create("http://localhost/"),
  $autoloader, "prod", FALSE
);
$kernel->boot();
\Drupal::service("module_installer")->install(["autosearch"]);
echo "autosearch module enabled\n";
'

echo "==> Enabling autosearch module..."
docker exec "$CONTAINER" php -r "$ENABLE_MODULE_PHP"

echo ""
echo "==> Visit: http://localhost:8080/autosearch"
