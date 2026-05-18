import argparse
import json
from pathlib import Path
from sentence_transformers import InputExample, SentenceTransformer, losses
from torch.utils.data import DataLoader

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from autosearch.config import AutoSearchConfig

REPO_ROOT = Path(__file__).parent.parent


def load_pairs(path: Path) -> list[InputExample]:
    examples = []
    with open(path) as f:
        for line in f:
            pair = json.loads(line)
            examples.append(InputExample(texts=[pair["query"], pair["item_text"]]))
    return examples


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(REPO_ROOT / "config.yaml"), type=Path)
    parser.add_argument("--local", action="store_true")
    args = parser.parse_args()

    cfg = AutoSearchConfig.from_yaml(args.config)
    output_dir = cfg.output_dir(local=args.local)
    examples = load_pairs(output_dir / "pairs-train.jsonl")
    print(f"Loaded {len(examples)} training pairs")

    model = SentenceTransformer(cfg.pipeline.base_model)
    dataloader = DataLoader(examples, shuffle=True, batch_size=32)
    loss = losses.MultipleNegativesRankingLoss(model)

    model.fit(
        train_objectives=[(dataloader, loss)],
        epochs=3,
        warmup_steps=min(100, len(examples) // 2),
        show_progress_bar=True,
        output_path=str(output_dir / "model"),
    )
    print(f"Model saved to {output_dir / 'model'}")


if __name__ == "__main__":
    main()
