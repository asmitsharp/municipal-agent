from pathlib import Path

from typer.testing import CliRunner

from muni.cli import app


runner = CliRunner()


def test_help_shows_command_groups():
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Municipal intelligence pipeline" in result.output
    assert "city" in result.output
    assert "run" in result.output
    assert "doctor" in result.output


def test_init_creates_workspace_files(tmp_path, monkeypatch):
    import muni.config as config

    monkeypatch.setattr(config, "PROJECT_ROOT", tmp_path)

    result = runner.invoke(app, ["init"])

    assert result.exit_code == 0
    assert (tmp_path / "configs" / "domains.yaml").exists()
    assert (tmp_path / "configs" / "ontology.yaml").exists()
    assert (tmp_path / "configs" / "cities").is_dir()
    assert (tmp_path / "data" / "raw").is_dir()
    assert (tmp_path / "data" / "processed").is_dir()
    assert (tmp_path / "data" / "charts").is_dir()
    assert (tmp_path / "data" / "exports").is_dir()


def test_doctor_runs_after_init(tmp_path, monkeypatch):
    import muni.config as config

    monkeypatch.setattr(config, "PROJECT_ROOT", tmp_path)
    runner.invoke(app, ["init"])

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "muni doctor" in result.output
    assert "Python" in result.output
    assert "Database" in result.output
    assert Path(tmp_path / "data").exists()

