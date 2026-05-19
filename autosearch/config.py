import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class CorpusConfig:
    id_field: str
    group_field: str
    name_field: str
    description_field: str


@dataclass
class PipelineConfig:
    base_model: str = "all-MiniLM-L6-v2"
    pairs_per_item: int = 10
    train_test_split: float = 0.8
    min_score_threshold: float = 0.4
    top_k: int = 5
    domain_description: str = "a user searching for information"


@dataclass
class StorageConfig:
    mode: str = "local"
    local_output_dir: str = "output/"
    s3_bucket: str = "autosearch-artefacts"
    s3_region: str = "ap-southeast-2"


@dataclass
class AutoSearchConfig:
    name: str
    corpus: CorpusConfig
    pipeline: PipelineConfig
    storage: StorageConfig

    def validate(self) -> None:
        if not self.name:
            raise ValueError("config.yaml: 'name' is required (non-empty string)")
        for fname in ("id_field", "group_field", "name_field"):
            val = getattr(self.corpus, fname)
            if not val:
                raise ValueError(f"config.yaml: 'corpus.{fname}' is required (non-empty string)")
        if self.pipeline.pairs_per_item <= 0:
            raise ValueError(
                f"config.yaml: 'pipeline.pairs_per_item' must be > 0 (got {self.pipeline.pairs_per_item})"
            )
        if not (0 < self.pipeline.train_test_split < 1):
            raise ValueError(
                f"config.yaml: 'pipeline.train_test_split' must be in (0, 1) (got {self.pipeline.train_test_split})"
            )
        if not (0 <= self.pipeline.min_score_threshold <= 1):
            raise ValueError(
                f"config.yaml: 'pipeline.min_score_threshold' must be in [0, 1] (got {self.pipeline.min_score_threshold})"
            )

    @classmethod
    def from_yaml(cls, path: Path) -> "AutoSearchConfig":
        data = yaml.safe_load(Path(path).read_text())
        c = data["corpus"]
        p = data.get("pipeline", {})
        s = data.get("storage", {})
        cfg = cls(
            name=data.get("name") or "",
            corpus=CorpusConfig(
                id_field=c.get("id_field") or "",
                group_field=c.get("group_field") or "",
                name_field=c.get("name_field") or "",
                description_field=c.get("description_field") or "",
            ),
            pipeline=PipelineConfig(
                base_model=p.get("base_model", "all-MiniLM-L6-v2"),
                pairs_per_item=p.get("pairs_per_item", 10),
                train_test_split=p.get("train_test_split", 0.8),
                min_score_threshold=p.get("min_score_threshold", 0.4),
                top_k=p.get("top_k", 5),
                domain_description=p.get("domain_description", "a user searching for information"),
            ),
            storage=StorageConfig(
                mode=s.get("mode", "local"),
                local_output_dir=s.get("local_output_dir", "output/"),
                s3_bucket=s.get("s3_bucket", "autosearch-artefacts"),
                s3_region=s.get("s3_region", "ap-southeast-2"),
            ),
        )
        cfg.validate()
        return cfg

    def output_dir(self, local: bool) -> Path:
        if local:
            return Path(self.storage.local_output_dir) / self.name
        raise NotImplementedError(
            "Non-local (S3) output is not implemented. Pass --local to all pipeline commands. "
            "StorageConfig.s3_bucket/s3_region fields are reserved for future use."
        )


def item_hash(item: dict, cfg: AutoSearchConfig) -> str:
    id_val = item[cfg.corpus.id_field]
    group_val = item[cfg.corpus.group_field]
    name_val = item[cfg.corpus.name_field]
    desc_val = item.get(cfg.corpus.description_field, "")
    payload = f"{group_val}:{id_val}:{name_val}:{desc_val}"
    return hashlib.sha256(payload.encode()).hexdigest()


def item_text(item: dict, cfg: AutoSearchConfig) -> str:
    name = item[cfg.corpus.name_field]
    desc = item.get(cfg.corpus.description_field, "")
    return f"{name} {desc}".strip() if desc else name
