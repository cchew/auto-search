<?php

namespace Drupal\autosearch\Controller;

use Drupal\Core\Controller\ControllerBase;

class AppController extends ControllerBase {

  public function page(): array {
    return [
      '#markup' => '<div id="app"></div>',
      '#attached' => [
        'library' => ['autosearch/autosearch_app'],
      ],
      // Do not cache: the shell bootstraps a dynamic SPA; a stale cached shell
      // would serve outdated JS to anonymous users after a module rebuild.
      '#cache' => [
        'max-age' => 0,
      ],
    ];
  }

}
