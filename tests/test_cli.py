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


def test_city_add_list_and_show(tmp_path, monkeypatch):
    import muni.config as config

    monkeypatch.setattr(config, "PROJECT_ROOT", tmp_path)
    runner.invoke(app, ["init"])

    add_result = runner.invoke(
        app,
        [
            "city",
            "add",
            "--slug",
            "lucknow",
            "--name",
            "Lucknow",
            "--state",
            "Uttar Pradesh",
            "--primary-language",
            "hindi",
            "--secondary-language",
            "english",
        ],
    )
    assert add_result.exit_code == 0
    assert (tmp_path / "configs" / "cities" / "lucknow.yaml").exists()

    list_result = runner.invoke(app, ["city", "list"])
    assert list_result.exit_code == 0
    assert "lucknow" in list_result.output
    assert "Lucknow" in list_result.output

    show_result = runner.invoke(app, ["city", "show", "--city", "lucknow"])
    assert show_result.exit_code == 0
    assert "Uttar Pradesh" in show_result.output
    assert "hindi" in show_result.output


def test_sources_add_list_and_domain_rejection(tmp_path, monkeypatch):
    import muni.config as config

    monkeypatch.setattr(config, "PROJECT_ROOT", tmp_path)
    runner.invoke(app, ["init"])
    runner.invoke(
        app,
        [
            "city",
            "add",
            "--slug",
            "lucknow",
            "--name",
            "Lucknow",
            "--state",
            "Uttar Pradesh",
        ],
    )

    add_result = runner.invoke(
        app,
        [
            "sources",
            "add",
            "--city",
            "lucknow",
            "--url",
            "https://lmc.up.nic.in",
            "--type",
            "municipal",
        ],
    )
    assert add_result.exit_code == 0
    assert "Registered source" in add_result.output

    list_result = runner.invoke(app, ["sources", "list", "--city", "lucknow"])
    assert list_result.exit_code == 0
    assert "municipal" in list_result.output
    assert "https://lmc.up.nic.in" in list_result.output

    reject_result = runner.invoke(
        app,
        [
            "sources",
            "add",
            "--city",
            "lucknow",
            "--url",
            "https://example.com/budget.pdf",
            "--type",
            "municipal",
        ],
    )
    assert reject_result.exit_code == 1
    assert "not whitelisted" in reject_result.output


def test_run_all_executes_agent_orchestrator(tmp_path, monkeypatch):
    import muni.config as config

    monkeypatch.setattr(config, "PROJECT_ROOT", tmp_path)

    result = runner.invoke(
        app,
        [
            "run",
            "all",
            "--city",
            "lucknow",
            "--name",
            "Lucknow",
            "--state",
            "Uttar Pradesh",
            "--municipal-url",
            "https://lmc.up.nic.in",
            "--years",
            "2019-20:2023-24",
        ],
    )

    assert result.exit_code == 0
    assert "Agent workflow:" in result.output
    assert "document_discovery" in result.output
    assert "document_classification" in result.output
    assert "narrative_synthesis" in result.output
    assert (tmp_path / "configs" / "cities" / "lucknow.yaml").exists()
