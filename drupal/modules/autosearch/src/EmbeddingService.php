<?php

namespace Drupal\autosearch;

use OnnxRuntime\InferenceSession;

/**
 * Embeds text using the fine-tuned ONNX model running in-process.
 *
 * Pipeline: BertTokenizer → ONNX inference → masked mean pooling → L2 norm.
 * Mirrors EmbeddingService.java and meanPoolAndNormalize() exactly so that
 * PHP and Java produce identical vectors for the same input.
 */
class EmbeddingService {

  private object $tokenizer;
  private string $modelPath;
  private ?InferenceSession $session = NULL;

  public function __construct(object $tokenizer, string $modelPath) {
    $this->tokenizer = $tokenizer;
    $this->modelPath = $modelPath;
  }

  /**
   * Returns a normalised float[] embedding for $text.
   *
   * @return float[]
   */
  public function embed(string $text): array {
    $enc = $this->tokenizer->encode($text);
    $session = $this->session();

    // ONNX Runtime PHP expects nested arrays: shape [1, seq_len].
    $inputs = [
      'input_ids'      => [$enc['input_ids']],
      'attention_mask' => [$enc['attention_mask']],
      'token_type_ids' => [$enc['token_type_ids']],
    ];

    $result = $session->run(NULL, $inputs);

    // result[0] is last_hidden_state: shape [1, seq_len, hidden_dim]
    // We need result[0][0]: shape [seq_len, hidden_dim]
    $hidden = $result[0][0];

    return $this->meanPoolAndNormalize($hidden, $enc['attention_mask']);
  }

  /**
   * Masked mean pooling then L2 normalisation — identical to Java implementation.
   *
   * @param float[][] $tokenEmbeddings shape [seq_len, hidden_dim]
   * @param int[]     $attentionMask   shape [seq_len]
   * @return float[]  normalised vector of length hidden_dim
   */
  private function meanPoolAndNormalize(array $tokenEmbeddings, array $attentionMask): array {
    $dim = count($tokenEmbeddings[0]);
    $pooled = array_fill(0, $dim, 0.0);
    $maskSum = 0.0;

    foreach ($tokenEmbeddings as $t => $row) {
      $m = (float) $attentionMask[$t];
      $maskSum += $m;
      for ($d = 0; $d < $dim; $d++) {
        $pooled[$d] += $row[$d] * $m;
      }
    }

    $denominator = max($maskSum, 1e-9);
    for ($d = 0; $d < $dim; $d++) {
      $pooled[$d] /= $denominator;
    }

    $norm = 0.0;
    foreach ($pooled as $v) {
      $norm += $v * $v;
    }
    $norm = sqrt($norm);

    if ($norm > 1e-9) {
      for ($d = 0; $d < $dim; $d++) {
        $pooled[$d] /= $norm;
      }
    }

    return $pooled;
  }

  private function session(): InferenceSession {
    if ($this->session === NULL) {
      $this->session = new InferenceSession($this->modelPath);
    }
    return $this->session;
  }

}
