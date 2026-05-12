import argparse
import json
from pathlib import Path
from sentence_transformers import InputExample, SentenceTransformer, losses
from torch.utils.data import DataLoader


def load_pairs(path: Path) -> list[InputExample]:
    examples = []
    with open(path) as f:
        for line in f:
            pair = json.loads(line)
            examples.append(InputExample(texts=[pair["query"], pair["item_text"]]))
    return examples


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true")
    args = parser.parse_args()

    output_dir = Path("output" if args.local else "/tmp/pipeline")
    examples = load_pairs(output_dir / "pairs-train.jsonl")
    print(f"Loaded {len(examples)} training pairs")

    model = SentenceTransformer("all-MiniLM-L6-v2")
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
