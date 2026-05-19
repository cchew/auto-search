import subprocess
import sys
from pathlib import Path

import click

REPO_ROOT = Path(__file__).parent.parent
FINE_TUNING = REPO_ROOT / "fine-tuning"
HARNESS = REPO_ROOT / "test-harness"


def _run(script: Path, extra_args: list[str]) -> None:
    subprocess.run([sys.executable, str(script)] + extra_args, check=True)


@click.group()
def cli():
    """Auto Search -- corpus-agnostic semantic search pipeline."""


@cli.command()
@click.option("--corpus", required=True, help="Path to corpus.json")
@click.option("--config", default=str(REPO_ROOT / "config.yaml"), help="Path to config.yaml")
@click.option("--local", is_flag=True, help="Write output locally instead of S3")
def generate(corpus, config, local):
    """Generate synthetic training pairs from corpus."""
    args = ["--corpus", corpus, "--config", config]
    if local:
        args.append("--local")
    _run(FINE_TUNING / "generate_pairs.py", args)


@cli.command()
@click.option("--config", default=str(REPO_ROOT / "config.yaml"), help="Path to config.yaml")
@click.option("--local", is_flag=True)
def train(config, local):
    """Fine-tune the embedding model on generated pairs."""
    args = ["--config", config]
    if local:
        args.append("--local")
    _run(FINE_TUNING / "train.py", args)


@cli.command()
@click.option("--config", default=str(REPO_ROOT / "config.yaml"), help="Path to config.yaml")
@click.option("--local", is_flag=True)
def export(config, local):
    """Export fine-tuned model to ONNX + INT8 quantisation."""
    args = ["--config", config]
    if local:
        args.append("--local")
    _run(FINE_TUNING / "export_onnx.py", args)


@cli.command()
@click.option("--corpus", required=True, help="Path to corpus.json")
@click.option("--config", default=str(REPO_ROOT / "config.yaml"), help="Path to config.yaml")
@click.option("--local", is_flag=True)
def embed(corpus, config, local):
    """Precompute and store corpus embeddings."""
    args = ["--corpus", corpus, "--config", config]
    if local:
        args.append("--local")
    _run(FINE_TUNING / "precompute_embeddings.py", args)


@cli.command()
@click.option("--corpus", required=True, help="Path to corpus.json")
@click.option("--queries", required=True, help="Path to test-queries.json")
@click.option("--config", default=str(REPO_ROOT / "config.yaml"), help="Path to config.yaml")
@click.option("--fine-tuned-model", default=None, help="Path to fine-tuned model directory")
def evaluate(corpus, queries, config, fine_tuned_model):
    """Evaluate model quality against test queries."""
    args = ["--corpus", corpus, "--queries", queries, "--config", config]
    if fine_tuned_model:
        args += ["--fine-tuned-model", fine_tuned_model]
    _run(HARNESS / "evaluate.py", args)


@cli.command(name="ui-config")
@click.option("--corpus", required=True, help="Path to corpus.json")
@click.option("--config", default=str(REPO_ROOT / "config.yaml"), help="Path to config.yaml")
@click.option("--local", is_flag=True, help="Write output locally instead of S3")
def ui_config(corpus, config, local):
    """Derive UI labels (title, lede, suggestions, group names) for the corpus."""
    import json
    from pathlib import Path
    import anthropic
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    from autosearch.config import AutoSearchConfig
    from autosearch.ui_config import derive_ui_config

    cfg = AutoSearchConfig.from_yaml(Path(config))
    corpus_items = json.loads(Path(corpus).read_text())
    client = anthropic.Anthropic()  # uses ANTHROPIC_API_KEY from env
    ui = derive_ui_config(corpus_items, cfg, client)

    out_dir = cfg.output_dir(local)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "corpus-ui.json"
    out_path.write_text(json.dumps(ui, indent=2))
    click.echo(f"Wrote {out_path}")


@cli.command()
@click.option("--corpus", required=True, help="Path to corpus.json")
@click.option("--config", default=str(REPO_ROOT / "config.yaml"), help="Path to config.yaml")
@click.option("--local", is_flag=True)
@click.option("--skip-train", is_flag=True, help="Skip model training (re-embed only)")
@click.option("--skip-ui-config", is_flag=True, help="Skip generating frontend UI labels")
@click.pass_context
def pipeline(ctx, corpus, config, local, skip_train, skip_ui_config):
    """Run the full pipeline: generate -> train -> export -> embed -> ui-config."""
    base = ["--config", config] + (["--local"] if local else [])
    _run(FINE_TUNING / "generate_pairs.py", ["--corpus", corpus] + base)
    if not skip_train:
        _run(FINE_TUNING / "train.py", base)
        _run(FINE_TUNING / "export_onnx.py", base)
    _run(FINE_TUNING / "precompute_embeddings.py", ["--corpus", corpus] + base)
    if not skip_ui_config:
        ctx.invoke(ui_config, corpus=corpus, config=config, local=local)
