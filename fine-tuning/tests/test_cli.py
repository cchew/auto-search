import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from click.testing import CliRunner
from autosearch.cli import cli


def test_cli_has_pipeline_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["pipeline", "--help"])
    assert result.exit_code == 0
    assert "--corpus" in result.output
    assert "--skip-train" in result.output


def test_cli_has_evaluate_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["evaluate", "--help"])
    assert result.exit_code == 0
    assert "--queries" in result.output


def test_cli_subcommands_exist():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    for cmd in ["generate", "train", "export", "embed", "evaluate", "pipeline"]:
        assert cmd in result.output
