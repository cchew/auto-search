<?php

namespace Drupal\autosearch;

use Normalizer;

/**
 * Pure-PHP BERT WordPiece tokenizer.
 *
 * Implements the same pipeline as the HuggingFace fast tokenizer shipped in
 * tokenizer.json: BertNormalizer (lowercase, clean_text, handle_chinese_chars,
 * strip_accents) → BertPreTokenizer → WordPiece → TemplateProcessing
 * ([CLS] + sequence + [SEP]) → truncation to max_length=256.
 *
 * Validated against Python HuggingFace output via tests/parity/.
 */
class BertTokenizer {

  private const MAX_LENGTH = 256;
  private const MAX_WORD_CHARS = 100;
  private const CLS_ID = 101;
  private const SEP_ID = 102;
  private const UNK_ID = 100;
  private const CONTINUATION_PREFIX = '##';

  /** @var array<string, int> token → id */
  private array $vocab;

  public function __construct(string $vocabPath) {
    $this->vocab = $this->loadVocab($vocabPath);
  }

  /**
   * Encodes text and returns arrays suitable for ONNX input.
   *
   * @return array{input_ids: int[], attention_mask: int[], token_type_ids: int[]}
   */
  public function encode(string $text): array {
    $normalized = $this->normalize($text);
    $words = $this->preTokenize($normalized);
    $ids = [self::CLS_ID];
    foreach ($words as $word) {
      foreach ($this->wordPiece($word) as $id) {
        $ids[] = $id;
        if (count($ids) >= self::MAX_LENGTH - 1) {
          break 2;
        }
      }
    }
    $ids[] = self::SEP_ID;

    $len = count($ids);
    return [
      'input_ids'      => $ids,
      'attention_mask' => array_fill(0, $len, 1),
      'token_type_ids' => array_fill(0, $len, 0),
    ];
  }

  // ── Normalizer ────────────────────────────────────────────────────────────

  private function normalize(string $text): string {
    $text = $this->cleanText($text);
    $text = $this->addCjkSpacing($text);
    $text = mb_strtolower($text, 'UTF-8');
    $text = $this->stripAccents($text);
    return $text;
  }

  /**
   * Replaces control characters and \r\n\t with a space; removes \0 and other
   * null-like control chars that BertNormalizer discards.
   */
  private function cleanText(string $text): string {
    $result = '';
    $len = mb_strlen($text, 'UTF-8');
    for ($i = 0; $i < $len; $i++) {
      $ch = mb_substr($text, $i, 1, 'UTF-8');
      $cp = $this->ord($ch);
      if ($cp === 0 || $cp === 0xFFFD) {
        continue;
      }
      if ($this->isControlChar($cp)) {
        $result .= ' ';
      }
      else {
        $result .= $ch;
      }
    }
    return $result;
  }

  private function isControlChar(int $cp): bool {
    if ($cp === 0x09 || $cp === 0x0A || $cp === 0x0D) {
      // Tab, newline, carriage return → treat as whitespace, not discarded
      return false;
    }
    $cat = $this->unicodeCategory($cp);
    return $cat === 'Cc' || $cat === 'Cf';
  }

  /**
   * Adds a space around every CJK Unified Ideograph character so that
   * BertPreTokenizer sees it as its own "word".
   */
  private function addCjkSpacing(string $text): string {
    $result = '';
    $len = mb_strlen($text, 'UTF-8');
    for ($i = 0; $i < $len; $i++) {
      $ch = mb_substr($text, $i, 1, 'UTF-8');
      if ($this->isCjkChar($this->ord($ch))) {
        $result .= ' ' . $ch . ' ';
      }
      else {
        $result .= $ch;
      }
    }
    return $result;
  }

  private function isCjkChar(int $cp): bool {
    return ($cp >= 0x4E00 && $cp <= 0x9FFF)
      || ($cp >= 0x3400 && $cp <= 0x4DBF)
      || ($cp >= 0x20000 && $cp <= 0x2A6DF)
      || ($cp >= 0x2A700 && $cp <= 0x2B73F)
      || ($cp >= 0x2B740 && $cp <= 0x2B81F)
      || ($cp >= 0x2B820 && $cp <= 0x2CEAF)
      || ($cp >= 0xF900 && $cp <= 0xFAFF)
      || ($cp >= 0x2F800 && $cp <= 0x2FA1F);
  }

  /**
   * NFD decomposition then drop combining marks (Unicode Mn category).
   * strip_accents=null with lowercase=true strips accents (matches Python).
   */
  private function stripAccents(string $text): string {
    $nfd = Normalizer::normalize($text, Normalizer::FORM_D);
    if ($nfd === FALSE) {
      return $text;
    }
    $result = '';
    $len = mb_strlen($nfd, 'UTF-8');
    for ($i = 0; $i < $len; $i++) {
      $ch = mb_substr($nfd, $i, 1, 'UTF-8');
      if ($this->unicodeCategory($this->ord($ch)) !== 'Mn') {
        $result .= $ch;
      }
    }
    return $result;
  }

  // ── PreTokenizer ──────────────────────────────────────────────────────────

  /**
   * BertPreTokenizer: split on whitespace, then split each token further on
   * punctuation boundaries (each punctuation char becomes its own token).
   *
   * @return string[]
   */
  private function preTokenize(string $text): array {
    $words = [];
    // Split on whitespace first.
    $rawWords = preg_split('/\s+/u', trim($text), -1, PREG_SPLIT_NO_EMPTY);
    if ($rawWords === FALSE) {
      return [];
    }
    foreach ($rawWords as $word) {
      // Further split on punctuation.
      foreach ($this->splitOnPunctuation($word) as $sub) {
        if ($sub !== '') {
          $words[] = $sub;
        }
      }
    }
    return $words;
  }

  /**
   * Splits a string at every punctuation character, yielding the punctuation
   * chars as separate tokens — mirrors Python's _run_split_on_punc.
   *
   * @return string[]
   */
  private function splitOnPunctuation(string $word): array {
    $parts = [];
    $current = '';
    $len = mb_strlen($word, 'UTF-8');
    for ($i = 0; $i < $len; $i++) {
      $ch = mb_substr($word, $i, 1, 'UTF-8');
      if ($this->isPunctuation($this->ord($ch))) {
        if ($current !== '') {
          $parts[] = $current;
          $current = '';
        }
        $parts[] = $ch;
      }
      else {
        $current .= $ch;
      }
    }
    if ($current !== '') {
      $parts[] = $current;
    }
    return $parts;
  }

  private function isPunctuation(int $cp): bool {
    // ASCII punctuation ranges.
    if (($cp >= 33 && $cp <= 47)
      || ($cp >= 58 && $cp <= 64)
      || ($cp >= 91 && $cp <= 96)
      || ($cp >= 123 && $cp <= 126)) {
      return TRUE;
    }
    $cat = $this->unicodeCategory($cp);
    return str_starts_with($cat, 'P');
  }

  // ── WordPiece ─────────────────────────────────────────────────────────────

  /**
   * Greedy longest-match WordPiece segmentation.
   *
   * @return int[] token ids
   */
  private function wordPiece(string $word): array {
    if (mb_strlen($word, 'UTF-8') > self::MAX_WORD_CHARS) {
      return [self::UNK_ID];
    }

    $chars = $this->mbStrSplit($word);
    $ids = [];
    $start = 0;
    $totalChars = count($chars);

    while ($start < $totalChars) {
      $end = $totalChars;
      $found = NULL;

      while ($start < $end) {
        $substr = implode('', array_slice($chars, $start, $end - $start));
        $lookup = ($start > 0) ? (self::CONTINUATION_PREFIX . $substr) : $substr;

        if (isset($this->vocab[$lookup])) {
          $found = $this->vocab[$lookup];
          break;
        }
        $end--;
      }

      if ($found === NULL) {
        return [self::UNK_ID];
      }

      $ids[] = $found;
      $start = $end;
    }

    return $ids;
  }

  // ── Helpers ───────────────────────────────────────────────────────────────

  private function loadVocab(string $path): array {
    $lines = file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    if ($lines === FALSE) {
      throw new \RuntimeException("Cannot read vocab file: $path");
    }
    $vocab = [];
    foreach ($lines as $id => $token) {
      $vocab[$token] = $id;
    }
    return $vocab;
  }

  /** Codepoint of a single UTF-8 character. */
  private function ord(string $ch): int {
    // mb_ord is available since PHP 7.2
    return mb_ord($ch, 'UTF-8') ?: 0;
  }

  /** Split a UTF-8 string into an array of individual characters. */
  private function mbStrSplit(string $str): array {
    $chars = [];
    $len = mb_strlen($str, 'UTF-8');
    for ($i = 0; $i < $len; $i++) {
      $chars[] = mb_substr($str, $i, 1, 'UTF-8');
    }
    return $chars;
  }

  /**
   * Returns the two-letter Unicode general category for a codepoint.
   * Uses IntlChar (PHP intl extension).
   */
  private function unicodeCategory(int $cp): string {
    $type = \IntlChar::charType($cp);
    // IntlChar::charType() returns integer constants; map to two-letter names.
    return match ($type) {
      \IntlChar::CHAR_CATEGORY_UPPERCASE_LETTER       => 'Lu',
      \IntlChar::CHAR_CATEGORY_LOWERCASE_LETTER       => 'Ll',
      \IntlChar::CHAR_CATEGORY_TITLECASE_LETTER       => 'Lt',
      \IntlChar::CHAR_CATEGORY_MODIFIER_LETTER        => 'Lm',
      \IntlChar::CHAR_CATEGORY_OTHER_LETTER           => 'Lo',
      \IntlChar::CHAR_CATEGORY_NON_SPACING_MARK       => 'Mn',
      \IntlChar::CHAR_CATEGORY_ENCLOSING_MARK         => 'Me',
      \IntlChar::CHAR_CATEGORY_COMBINING_SPACING_MARK => 'Mc',
      \IntlChar::CHAR_CATEGORY_DECIMAL_DIGIT_NUMBER   => 'Nd',
      \IntlChar::CHAR_CATEGORY_LETTER_NUMBER          => 'Nl',
      \IntlChar::CHAR_CATEGORY_OTHER_NUMBER           => 'No',
      \IntlChar::CHAR_CATEGORY_SPACE_SEPARATOR        => 'Zs',
      \IntlChar::CHAR_CATEGORY_LINE_SEPARATOR         => 'Zl',
      \IntlChar::CHAR_CATEGORY_PARAGRAPH_SEPARATOR    => 'Zp',
      \IntlChar::CHAR_CATEGORY_CONTROL_CHAR           => 'Cc',
      \IntlChar::CHAR_CATEGORY_FORMAT_CHAR            => 'Cf',
      \IntlChar::CHAR_CATEGORY_PRIVATE_USE_CHAR       => 'Co',
      \IntlChar::CHAR_CATEGORY_SURROGATE              => 'Cs',
      \IntlChar::CHAR_CATEGORY_DASH_PUNCTUATION       => 'Pd',
      \IntlChar::CHAR_CATEGORY_START_PUNCTUATION      => 'Ps',
      \IntlChar::CHAR_CATEGORY_END_PUNCTUATION        => 'Pe',
      \IntlChar::CHAR_CATEGORY_CONNECTOR_PUNCTUATION  => 'Pc',
      \IntlChar::CHAR_CATEGORY_OTHER_PUNCTUATION      => 'Po',
      \IntlChar::CHAR_CATEGORY_MATH_SYMBOL            => 'Sm',
      \IntlChar::CHAR_CATEGORY_CURRENCY_SYMBOL        => 'Sc',
      \IntlChar::CHAR_CATEGORY_MODIFIER_SYMBOL        => 'Sk',
      \IntlChar::CHAR_CATEGORY_OTHER_SYMBOL           => 'So',
      \IntlChar::CHAR_CATEGORY_INITIAL_PUNCTUATION    => 'Pi',
      \IntlChar::CHAR_CATEGORY_FINAL_PUNCTUATION      => 'Pf',
      default                                         => 'Cn',
    };
  }

}
