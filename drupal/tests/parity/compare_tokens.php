<?php

/**
 * Parity test: compare BertTokenizer.php output against Python reference.
 *
 * Run inside Docker (where intl and the module autoloader are available):
 *   docker compose exec drupal php modules/custom/autosearch/../../tests/parity/compare_tokens.php
 *
 * Or run standalone (needs intl extension and the module src on the include path):
 *   php -d extension=intl tests/parity/compare_tokens.php
 */

declare(strict_types=1);

// When run standalone (outside Drupal), bootstrap the tokenizer directly.
if (!class_exists('Drupal\autosearch\BertTokenizer')) {
    require_once __DIR__ . '/../../modules/autosearch/src/BertTokenizer.php';
}

use Drupal\autosearch\BertTokenizer;

$vocabPath     = getenv('AUTOSEARCH_VOCAB_PATH') ?: __DIR__ . '/../../../../repo/output/it-service-catalogue/artefacts/vocab.txt';
$referencePath = getenv('AUTOSEARCH_REFERENCE_PATH') ?: __DIR__ . '/reference.json';

if (!file_exists($referencePath)) {
    fwrite(STDERR, "reference.json not found — run generate_reference.py first\n");
    exit(1);
}

$tokenizer = new BertTokenizer($vocabPath);
$cases     = json_decode(file_get_contents($referencePath), true, 512, JSON_THROW_ON_ERROR);

$pass = 0;
$fail = 0;

foreach ($cases as $case) {
    $enc = $tokenizer->encode($case['text']);

    $idsMatch  = $enc['input_ids'] === $case['input_ids'];
    $maskMatch = $enc['attention_mask'] === $case['attention_mask'];
    $typeMatch = $enc['token_type_ids'] === $case['token_type_ids'];

    if ($idsMatch && $maskMatch && $typeMatch) {
        echo "PASS  " . json_encode($case['text']) . "\n";
        $pass++;
    } else {
        echo "FAIL  " . json_encode($case['text']) . "\n";
        if (!$idsMatch) {
            echo "  expected ids: " . implode(',', $case['input_ids']) . "\n";
            echo "  actual   ids: " . implode(',', $enc['input_ids']) . "\n";
        }
        if (!$maskMatch) {
            echo "  mask mismatch\n";
        }
        if (!$typeMatch) {
            echo "  type_ids mismatch\n";
        }
        $fail++;
    }
}

echo "\n$pass passed, $fail failed\n";
exit($fail > 0 ? 1 : 0);
