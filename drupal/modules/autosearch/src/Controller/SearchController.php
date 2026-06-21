<?php

namespace Drupal\autosearch\Controller;

use Drupal\Core\Controller\ControllerBase;
use Symfony\Component\DependencyInjection\ContainerInterface;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;

class SearchController extends ControllerBase {

  public function __construct(
    private readonly object $embedding,
    private readonly object $similarity,
  ) {}

  public static function create(ContainerInterface $container): static {
    return new static(
      $container->get('autosearch.embedding'),
      $container->get('autosearch.similarity'),
    );
  }

  public function search(Request $request): JsonResponse {
    $body = json_decode($request->getContent(), TRUE);
    $query = trim((string) ($body['query'] ?? ''));
    $topK  = max(1, min(20, (int) ($body['topK'] ?? 5)));

    if ($query === '') {
      return new JsonResponse(['error' => 'query is required'], 400);
    }

    try {
      $vec     = $this->embedding->embed($query);
      $results = $this->similarity->search($vec, $topK);
      return new JsonResponse($results);
    }
    catch (\Throwable $e) {
      \Drupal::logger('autosearch')->error('Search failed: @msg', ['@msg' => $e->getMessage()]);
      return new JsonResponse(['error' => 'search failed'], 500);
    }
  }

  public function health(): JsonResponse {
    return new JsonResponse(['status' => 'UP']);
  }

}
