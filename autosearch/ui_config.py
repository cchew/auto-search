"""Derive frontend UI labels (title, lede, suggestions, group names) for a corpus."""

import json
from typing import Any, Protocol

from autosearch.config import AutoSearchConfig


class _AnthropicLike(Protocol):
    """Subset of anthropic.Anthropic we depend on (allows test fakes)."""
    messages: Any


def _call(client: _AnthropicLike, prompt: str) -> str:
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return text


def _labels_prompt(group_samples: dict[int, list[str]], domain: str) -> str:
    groups_block = "\n".join(
        f"  Group {gid}: {', '.join(sorted(set(titles))[:5])}"
        for gid, titles in sorted(group_samples.items())
    )
    return (
        f"You are labelling a domain-specific data catalogue for a frontend UI.\n"
        f"Domain: {domain}\n"
        f"Groups (with example item titles):\n{groups_block}\n\n"
        f"Return a JSON object with keys:\n"
        f"  appTitle: short product-style title (3-6 words)\n"
        f"  appLede: one sentence describing what users can search for\n"
        f"  groupNames: object mapping each group id (as a string) to a 1-4 word label\n"
        f"Return JSON only, no commentary."
    )


def _suggestions_prompt(sample_titles: list[str], domain: str) -> str:
    sample = "\n".join(f"  - {t}" for t in sample_titles[:20])
    return (
        f"Suggest 4 natural-language search queries an end user might type to find items in this catalogue.\n"
        f"Mix exact intent and paraphrase. Keep them short.\n"
        f"Domain: {domain}\n"
        f"Sample items:\n{sample}\n\n"
        f"Return a JSON array of 4 strings only."
    )


def derive_ui_config(
    corpus: list[dict],
    cfg: AutoSearchConfig,
    client: _AnthropicLike,
) -> dict:
    """Derive a corpus-ui.json payload from a corpus + Anthropic client."""
    group_samples: dict[int, list[str]] = {}
    titles: list[str] = []
    for item in corpus:
        gid = int(item[cfg.corpus.group_field])
        name = str(item[cfg.corpus.name_field])
        group_samples.setdefault(gid, []).append(name)
        titles.append(name)

    labels = json.loads(_call(client, _labels_prompt(group_samples, cfg.pipeline.domain_description)))
    suggestions = json.loads(_call(client, _suggestions_prompt(titles, cfg.pipeline.domain_description)))

    group_names: dict[str, str] = {}
    for gid in group_samples:
        key = str(gid)
        group_names[key] = labels.get("groupNames", {}).get(key, f"Group {gid}")

    return {
        "appTitle": labels["appTitle"],
        "appLede": labels["appLede"],
        "suggestions": suggestions,
        "groupNames": group_names,
    }
