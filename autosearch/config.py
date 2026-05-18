import hashlib
from dataclasses import dataclass
from pathlib import Path

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

    @classmethod
    def from_yaml(cls, path: Path) -> "AutoSearchConfig":
        data = yaml.safe_load(Path(path).read_text())
        c = data["corpus"]
        p = data.get("pipeline", {})
        s = data.get("storage", {})
        return cls(
            name=data.get("name", "default"),
            corpus=CorpusConfig(
                id_field=c["id_field"],
                group_field=c["group_field"],
                name_field=c["name_field"],
                description_field=c["description_field"],
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

    def output_dir(self, local: bool) -> Path:
        if local:
            return Path(self.storage.local_output_dir) / self.name
        return Path("/tmp/pipeline") / self.name


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
