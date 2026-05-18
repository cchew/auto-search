import argparse
import shutil
from pathlib import Path

from optimum.onnxruntime import ORTModelForFeatureExtraction
from onnxruntime.quantization import QuantType, quantize_dynamic
from transformers import AutoTokenizer

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from autosearch.config import AutoSearchConfig

REPO_ROOT = Path(__file__).parent.parent


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(REPO_ROOT / "config.yaml"), type=Path)
    parser.add_argument("--local", action="store_true")
    args = parser.parse_args()

    cfg = AutoSearchConfig.from_yaml(args.config)
    output_dir = cfg.output_dir(local=args.local)
    model_path = output_dir / "model"
    onnx_dir = output_dir / "onnx"
    artefacts_dir = output_dir / "artefacts"
    onnx_dir.mkdir(parents=True, exist_ok=True)
    artefacts_dir.mkdir(parents=True, exist_ok=True)

    print("Exporting to ONNX...")
    model = ORTModelForFeatureExtraction.from_pretrained(
        str(model_path), export=True, provider="CPUExecutionProvider"
    )
    tokenizer = AutoTokenizer.from_pretrained(str(model_path))
    model.save_pretrained(str(onnx_dir))
    tokenizer.save_pretrained(str(onnx_dir))

    print("Applying INT8 quantisation...")
    quantize_dynamic(
        str(onnx_dir / "model.onnx"),
        str(artefacts_dir / "autosearch-embed.onnx"),
        weight_type=QuantType.QInt8,
    )

    for filename in ("tokenizer.json", "tokenizer_config.json", "vocab.txt", "special_tokens_map.json"):
        src = onnx_dir / filename
        if src.exists():
            shutil.copy(src, artefacts_dir / filename)
        else:
            print(f"  Warning: {filename} not found in {onnx_dir}, skipping")

    print(f"Artefacts written to {artefacts_dir}")
    print(f"  {artefacts_dir / 'autosearch-embed.onnx'}")
    print(f"  {artefacts_dir / 'tokenizer.json'}")


if __name__ == "__main__":
    main()
