<?php

namespace Drupal\autosearch;

/**
 * Loads pre-computed corpus embeddings and returns top-K cosine matches.
 *
 * Vectors are L2-normalised at embed time, so cosine similarity = dot product.
 * Mirrors SimilarityService.java exactly.
 *
 * Field names (idField, groupField, nameField) are read from the corpus
 * ui-config.json so the module works with any corpus without extra config.
 */
class SimilarityService {

  private float $minScore;
  private string $embeddingsPath;
  private string $uiConfigPath;

  /** @var list<array{item_id: int, group_id: int, name: string, embedding: float[]}> */
  private ?array $items = NULL;

  public function __construct(string $embeddingsPath, float $minScore, string $uiConfigPath) {
    $this->embeddingsPath = $embeddingsPath;
    $this->minScore = $minScore;
    $this->uiConfigPath = $uiConfigPath;
  }

  /**
   * Returns top-K results above minScore threshold, sorted by score desc.
   *
   * @param float[] $queryVector Normalised query embedding.
   * @return list<array{group_id: int, item_id: int, name: string, score: float}>
   */
  public function search(array $queryVector, int $topK = 5): array {
    $scored = [];
    foreach ($this->items() as $item) {
      $scored[] = [
        'group_id' => $item['group_id'],
        'item_id'  => $item['item_id'],
        'name'     => $item['name'],
        'score'    => $this->dot($queryVector, $item['embedding']),
      ];
    }

    usort($scored, fn($a, $b) => $b['score'] <=> $a['score']);

    $results = [];
    foreach (array_slice($scored, 0, $topK) as $s) {
      if ($s['score'] < $this->minScore) {
        break;
      }
      $results[] = $s;
    }

    return $results;
  }

  /**
   * @param float[] $a
   * @param float[] $b
   */
  private function dot(array $a, array $b): float {
    $sum = 0.0;
    $len = count($a);
    for ($i = 0; $i < $len; $i++) {
      $sum += $a[$i] * $b[$i];
    }
    return $sum;
  }

  /** @return list<array{item_id: int, group_id: int, name: string, embedding: float[]}> */
  private function items(): array {
    if ($this->items === NULL) {
      $fields = $this->fieldNames();
      $json = file_get_contents($this->embeddingsPath);
      if ($json === FALSE) {
        throw new \RuntimeException("Cannot read embeddings: {$this->embeddingsPath}");
      }
      $raw = json_decode($json, TRUE, 512, JSON_THROW_ON_ERROR);
      $this->items = array_map(
        fn($m) => [
          'item_id'   => (int) $m[$fields['id']],
          'group_id'  => (int) $m[$fields['group']],
          'name'      => (string) $m[$fields['name']],
          'embedding' => array_map('floatval', $m['embedding']),
        ],
        $raw
      );
    }
    return $this->items;
  }

  /** @return array{id: string, group: string, name: string} */
  private function fieldNames(): array {
    $json = file_get_contents($this->uiConfigPath);
    if ($json === FALSE) {
      // Sensible fallback matching the health-workforce corpus.
      return ['id' => 'item_id', 'group' => 'group_id', 'name' => 'name'];
    }
    $cfg = json_decode($json, TRUE, 512, JSON_THROW_ON_ERROR);
    return [
      'id'    => $cfg['idField']    ?? 'item_id',
      'group' => $cfg['groupField'] ?? 'group_id',
      'name'  => $cfg['nameField']  ?? 'name',
    ];
  }

}
