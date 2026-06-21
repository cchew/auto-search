<?php

namespace Drupal\autosearch\Controller;

use Drupal\Core\Controller\ControllerBase;
use Symfony\Component\HttpFoundation\JsonResponse;

class CorpusController extends ControllerBase {

  private function modelPath(string $file): string {
    $config = \Drupal::config('autosearch.settings');
    $overrideKey = str_replace(['.json', '-'], ['_path', '_'], $file);
    $override = $config->get($overrideKey);
    if ($override) {
      return \Drupal::root() . '/' . $override;
    }
    return \Drupal::root() . '/modules/custom/autosearch/model/' . $file;
  }

  public function corpus(): JsonResponse {
    return $this->serveJsonFile($this->modelPath('corpus.json'));
  }

  public function uiConfig(): JsonResponse {
    return $this->serveJsonFile($this->modelPath('ui-config.json'));
  }

  private function serveJsonFile(string $path): JsonResponse {
    if (!file_exists($path)) {
      return new JsonResponse(['error' => 'not found'], 404);
    }
    $json = file_get_contents($path);
    if ($json === FALSE) {
      return new JsonResponse(['error' => 'read error'], 500);
    }
    try {
      $data = json_decode($json, TRUE, 512, JSON_THROW_ON_ERROR);
    }
    catch (\JsonException $e) {
      return new JsonResponse(['error' => 'invalid json', 'detail' => $e->getMessage()], 500);
    }
    return new JsonResponse($data);
  }

}
