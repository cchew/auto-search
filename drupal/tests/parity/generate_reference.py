#!/usr/bin/env python3
"""
Generate reference token IDs using the real HuggingFace tokenizer.

Output: tests/parity/reference.json — a list of test cases each with
  { "text": ..., "input_ids": [...], "attention_mask": [...], "token_type_ids": [...] }

Run from the drupal/ directory:
  cd projects/auto-search/drupal
  python3 tests/parity/generate_reference.py
"""

import json
import sys
from pathlib import Path

# Reuse the auto-search Python venv which already has tokenizers installed.
AUTOSEARCH_VENV = Path(__file__).resolve().parents[3] / "repo" / ".venv" / "lib"
venv_site_packages = sorted(AUTOSEARCH_VENV.glob("python3.*"))
if venv_site_packages:
    sys.path.insert(0, str(venv_site_packages[-1] / "site-packages"))

from tokenizers import Tokenizer  # type: ignore

TOKENIZER_PATH = Path(__file__).resolve().parents[3] / "repo" / "output" / "it-service-catalogue" / "artefacts" / "tokenizer.json"

TEST_STRINGS = [
    "GP FTE",
    "doctor hours",
    "general practitioner full-time equivalent",
    "total nursing workforce",
    "what is the average salary of a physiotherapist",
    "café résumé",
    "IT service desk support",
    "network infrastructure",
    "Hello, World!",
    "   multiple   spaces   ",
    "数据科学家",
    "simple",
    "un-hyphenated",
    "UPPERCASE TEXT",
]

def main() -> None:
    tok = Tokenizer.from_file(str(TOKENIZER_PATH))
    tok.enable_truncation(max_length=256)
    tok.no_padding()

    cases = []
    for text in TEST_STRINGS:
        enc = tok.encode(text)
        cases.append({
            "text": text,
            "input_ids": enc.ids,
            "attention_mask": enc.attention_mask,
            "token_type_ids": enc.type_ids,
        })

    out = Path(__file__).parent / "reference.json"
    out.write_text(json.dumps(cases, indent=2, ensure_ascii=False))
    print(f"Wrote {len(cases)} test cases to {out}")

if __name__ == "__main__":
    main()
