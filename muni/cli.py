import platform
import shutil
import sys
from pathlib import Path
from typing import List, Optional, Tuple

import typer
from rich.table import Table

from muni.cities.service import (
    CityProfileError,
    add_official_source,
    create_city_profile,
    list_city_profiles,
    load_city_profile,
)
from muni.config import get_settings, initialize_default_configs, load_yaml
from muni.console import console
from muni.db.session import check_database, check_postgis
from muni.sources.whitelist import DomainWhitelistError, validate_source_url

app = typer.Typer(
    help="Municipal intelligence pipeline for Indian cities.",
    no_args_is_help=True,
)

city_app = typer.Typer(help="Manage city profiles.", no_args_is_help=True)
sources_app = typer.Typer(help="Manage official source URLs.", no_args_is_help=True)
docs_app = typer.Typer(help="Inspect ingested documents.", no_args_is_help=True)
review_app = typer.Typer(help="Inspect and resolve review items.", no_args_is_help=True)
ontology_app = typer.Typer(help="Manage ontology mappings.", no_args_is_help=True)
metrics_app = typer.Typer(help="Inspect computed metrics.", no_args_is_help=True)
evidence_app = typer.Typer(help="Trace metrics and facts to source evidence.", no_args_is_help=True)
governance_app = typer.Typer(help="Build governance responsibility maps.", no_args_is_help=True)
spatial_app = typer.Typer(help="Manage spatial layers.", no_args_is_help=True)
anomalies_app = typer.Typer(help="Run and inspect anomaly detection.", no_args_is_help=True)
visualize_app = typer.Typer(help="Generate publication-ready charts.", no_args_is_help=True)
narrative_app = typer.Typer(help="Generate evidence-backed narrative drafts.", no_args_is_help=True)
run_app = typer.Typer(help="Run bundled workflows.", no_args_is_help=True)

app.add_typer(city_app, name="city")
app.add_typer(sources_app, name="sources")
app.add_typer(docs_app, name="docs")
app.add_typer(review_app, name="review")
app.add_typer(ontology_app, name="ontology")
app.add_typer(metrics_app, name="metrics")
app.add_typer(evidence_app, name="evidence")
app.add_typer(governance_app, name="governance")
app.add_typer(spatial_app, name="spatial")
app.add_typer(anomalies_app, name="anomalies")
app.add_typer(visualize_app, name="visualize")
app.add_typer(narrative_app, name="narrative")
app.add_typer(run_app, name="run")


def _status_table(title: str, rows: List[Tuple[str, str, str]]) -> None:
    table = Table(title=title)
    table.add_column("Check", style="bold")
    table.add_column("Status")
    table.add_column("Detail")
    for name, status, detail in rows:
        style = "green" if status == "OK" else "yellow" if status in {"SKIP", "WARN"} else "red"
        table.add_row(name, f"[{style}]{status}[/{style}]", detail)
    console.print(table)


def _placeholder(command_name: str) -> None:
    console.print(f"[yellow]{command_name} is planned but not implemented in Phase 0.[/yellow]")
    raise typer.Exit(code=2)


@app.command()
def init() -> None:
    """Create local config files and data directories."""
    settings = get_settings()
    created = initialize_default_configs(settings)

    console.print("[bold green]Initialized municipal intelligence workspace.[/bold green]")
    console.print(f"Config directory: {settings.config_dir}")
    console.print(f"Data directory: {settings.data_dir}")

    for name, was_created in created.items():
        action = "created" if was_created else "exists"
        console.print(f"- {name}: {action}")


@app.command()
def doctor(strict: bool = typer.Option(False, help="Exit non-zero when optional tools are missing.")) -> None:
    """Check runtime dependencies and local workspace readiness."""
    settings = get_settings()
    rows: List[Tuple[str, str, str]] = []
    failures = 0

    py_version = platform.python_version()
    if sys.version_info >= (3, 8):
        rows.append(("Python", "OK", py_version))
    else:
        rows.append(("Python", "FAIL", f"{py_version}; requires >= 3.8"))
        failures += 1

    for path in [
        settings.config_dir,
        settings.city_config_dir,
        settings.data_dir,
        settings.raw_data_dir,
        settings.processed_data_dir,
        settings.charts_dir,
        settings.exports_dir,
    ]:
        if path.exists() and path.is_dir():
            rows.append((str(path.relative_to(settings.project_root)), "OK", "directory exists"))
        else:
            rows.append((str(path.relative_to(settings.project_root)), "WARN", "run `muni init`"))

    try:
        check_database(settings.database_url)
        rows.append(("Database", "OK", settings.database_url))
    except Exception as exc:
        rows.append(("Database", "FAIL", f"{exc.__class__.__name__}: {exc}"))
        failures += 1

    try:
        postgis_status = check_postgis(settings.database_url)
        status = "SKIP" if postgis_status.startswith("skipped:") else "OK"
        rows.append(("PostGIS", status, postgis_status))
    except Exception as exc:
        rows.append(("PostGIS", "FAIL", f"{exc.__class__.__name__}: {exc}"))
        failures += 1

    for executable, label in [
        ("tesseract", "Tesseract"),
        ("java", "Java for Tabula"),
    ]:
        found = shutil.which(executable)
        if found:
            rows.append((label, "OK", found))
        else:
            rows.append((label, "WARN", f"`{executable}` not found"))
            if strict:
                failures += 1

    domains_config = settings.config_dir / "domains.yaml"
    try:
        domains = load_yaml(domains_config)
        count = len(domains.get("allowed_domains", []))
        rows.append(("Domain config", "OK", f"{count} allowed domain rules"))
    except Exception as exc:
        rows.append(("Domain config", "WARN", f"{exc.__class__.__name__}: {exc}"))
        if strict:
            failures += 1

    _status_table("muni doctor", rows)
    if failures:
        raise typer.Exit(code=1)


@city_app.command("add")
def city_add(
    slug: str = typer.Option(..., help="Stable city slug, for example `lucknow`."),
    name: str = typer.Option(..., help="Human-readable city name."),
    state: str = typer.Option(..., help="Indian state or union territory."),
    country: str = typer.Option("India", help="Country name."),
    fiscal_year_format: str = typer.Option("april_march", help="Fiscal year convention."),
    primary_language: Optional[str] = typer.Option(None, help="Primary document language."),
    secondary_language: Optional[str] = typer.Option(None, help="Secondary document language."),
) -> None:
    try:
        profile = create_city_profile(
            slug=slug,
            name=name,
            state=state,
            country=country,
            fiscal_year_format=fiscal_year_format,
            primary_language=primary_language,
            secondary_language=secondary_language,
        )
    except CityProfileError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1)

    console.print(f"[green]Created city profile:[/green] {profile.slug}")
    console.print(f"Path: {get_settings().city_config_dir / f'{profile.slug}.yaml'}")


@city_app.command("list")
def city_list() -> None:
    profiles = list_city_profiles()
    table = Table(title="City profiles")
    table.add_column("Slug", style="bold")
    table.add_column("Name")
    table.add_column("State")
    table.add_column("Sources", justify="right")
    for profile in profiles:
        table.add_row(
            profile.slug,
            profile.name,
            profile.state,
            str(len(profile.official_sources)),
        )
    console.print(table)


@city_app.command("show")
def city_show(city: str = typer.Option(..., help="City slug.")) -> None:
    try:
        profile = load_city_profile(city)
    except CityProfileError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1)

    table = Table(title=f"City profile: {profile.slug}")
    table.add_column("Field", style="bold")
    table.add_column("Value")
    table.add_row("Name", profile.name)
    table.add_row("State", profile.state)
    table.add_row("Country", profile.country)
    table.add_row("Fiscal year", profile.fiscal_year_format)
    table.add_row("Primary language", profile.primary_language or "")
    table.add_row("Secondary language", profile.secondary_language or "")
    table.add_row("Official sources", str(len(profile.official_sources)))
    table.add_row("Known agencies", str(len(profile.known_agencies)))
    console.print(table)

    if profile.official_sources:
        sources_table = Table(title="Official sources")
        sources_table.add_column("Type", style="bold")
        sources_table.add_column("URL")
        for source in profile.official_sources:
            sources_table.add_row(source.type, source.url)
        console.print(sources_table)


@sources_app.command("add")
def sources_add(
    city: str = typer.Option(..., help="City slug."),
    url: str = typer.Option(..., help="Official source URL."),
    source_type: str = typer.Option(..., "--type", help="Source type."),
) -> None:
    try:
        validated_url = validate_source_url(url)
        profile = add_official_source(city, validated_url, source_type)
    except (CityProfileError, DomainWhitelistError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1)

    console.print(f"[green]Registered source for {profile.slug}:[/green] {validated_url}")


@sources_app.command("list")
def sources_list(city: str = typer.Option(..., help="City slug.")) -> None:
    try:
        profile = load_city_profile(city)
    except CityProfileError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1)

    table = Table(title=f"Official sources: {profile.slug}")
    table.add_column("Type", style="bold")
    table.add_column("URL")
    for source in profile.official_sources:
        table.add_row(source.type, source.url)
    console.print(table)


@app.command()
def discover(city: str = typer.Option(..., help="City slug.")) -> None:
    _placeholder(f"muni discover --city {city}")


@app.command()
def ingest(city: str = typer.Option(..., help="City slug."), path: Path = typer.Option(...)) -> None:
    _placeholder(f"muni ingest --city {city} --path {path}")


@app.command()
def classify(city: str = typer.Option(..., help="City slug.")) -> None:
    _placeholder(f"muni classify --city {city}")


@app.command()
def extract(
    city: str = typer.Option(..., help="City slug."),
    doc_id: Optional[str] = typer.Option(None, help="Document ID."),
    priority: Optional[str] = typer.Option(None, help="Priority such as P1."),
) -> None:
    target = f"--doc-id {doc_id}" if doc_id else f"--priority {priority}"
    _placeholder(f"muni extract --city {city} {target}")


@app.command()
def normalize(city: str = typer.Option(..., help="City slug.")) -> None:
    _placeholder(f"muni normalize --city {city}")


@app.command()
def analyze(city: str = typer.Option(..., help="City slug."), years: str = typer.Option(...)) -> None:
    _placeholder(f"muni analyze --city {city} --years {years}")


@docs_app.command("list")
def docs_list(city: str = typer.Option(..., help="City slug."), priority: Optional[str] = None) -> None:
    _placeholder(f"muni docs list --city {city} --priority {priority}")


@docs_app.command("show")
def docs_show(doc_id: str) -> None:
    _placeholder(f"muni docs show {doc_id}")


@review_app.command("queue")
def review_queue(city: str = typer.Option(..., help="City slug.")) -> None:
    _placeholder(f"muni review queue --city {city}")


@review_app.command("approve")
def review_approve(review_id: str) -> None:
    _placeholder(f"muni review approve {review_id}")


@ontology_app.command("unmapped")
def ontology_unmapped(city: str = typer.Option(..., help="City slug.")) -> None:
    _placeholder(f"muni ontology unmapped --city {city}")


@ontology_app.command("approve")
def ontology_approve(mapping_id: str) -> None:
    _placeholder(f"muni ontology approve {mapping_id}")


@metrics_app.command("table")
def metrics_table(city: str = typer.Option(..., help="City slug.")) -> None:
    _placeholder(f"muni metrics table --city {city}")


@evidence_app.command("show")
def evidence_show(
    metric: str = typer.Option(..., help="Metric name."),
    city: str = typer.Option(..., help="City slug."),
    year: str = typer.Option(..., help="Fiscal year."),
) -> None:
    _placeholder(f"muni evidence show --metric {metric} --city {city} --year {year}")


@app.command()
def trace(record_id: str) -> None:
    _placeholder(f"muni trace {record_id}")


@governance_app.command("map")
def governance_map(city: str = typer.Option(..., help="City slug.")) -> None:
    _placeholder(f"muni governance map --city {city}")


@governance_app.command("service")
def governance_service(city: str = typer.Option(...), service: str = typer.Option(...)) -> None:
    _placeholder(f"muni governance service --city {city} --service {service}")


@spatial_app.command("ingest")
def spatial_ingest(city: str = typer.Option(...), layer: str = typer.Option(...), path: Path = typer.Option(...)) -> None:
    _placeholder(f"muni spatial ingest --city {city} --layer {layer} --path {path}")


@spatial_app.command("layers")
def spatial_layers(city: str = typer.Option(...)) -> None:
    _placeholder(f"muni spatial layers --city {city}")


@spatial_app.command("join-tax")
def spatial_join_tax(city: str = typer.Option(...)) -> None:
    _placeholder(f"muni spatial join-tax --city {city}")


@anomalies_app.command("run")
def anomalies_run(city: str = typer.Option(...)) -> None:
    _placeholder(f"muni anomalies run --city {city}")


@anomalies_app.command("list")
def anomalies_list(city: str = typer.Option(...)) -> None:
    _placeholder(f"muni anomalies list --city {city}")


@anomalies_app.command("explain")
def anomalies_explain(anomaly_id: str) -> None:
    _placeholder(f"muni anomalies explain {anomaly_id}")


@visualize_app.command("one")
def visualize_one(city: str = typer.Option(...), chart: str = typer.Option(...), year: Optional[str] = None) -> None:
    _placeholder(f"muni visualize one --city {city} --chart {chart} --year {year}")


@visualize_app.callback(invoke_without_command=True)
def visualize(
    ctx: typer.Context,
    city: Optional[str] = typer.Option(None, help="City slug."),
    pack: Optional[str] = typer.Option(None, help="Visualization pack."),
) -> None:
    if ctx.invoked_subcommand is None:
        _placeholder(f"muni visualize --city {city} --pack {pack}")


@narrative_app.command("draft")
def narrative_draft(city: str = typer.Option(...), output_format: str = typer.Option(..., "--format")) -> None:
    _placeholder(f"muni narrative draft --city {city} --format {output_format}")


@app.command()
def export(city: str = typer.Option(...), bundle: str = typer.Option(...)) -> None:
    _placeholder(f"muni export --city {city} --bundle {bundle}")


@run_app.command("all")
def run_all(
    city: str = typer.Option(..., help="City slug."),
    years: str = typer.Option(..., help="Fiscal year range."),
    name: Optional[str] = typer.Option(None, help="City name for first-time setup."),
    state: Optional[str] = typer.Option(None, help="State for first-time setup."),
    municipal_url: Optional[str] = typer.Option(None, help="Official municipal URL."),
    allow_review_gaps: bool = typer.Option(False, help="Continue despite critical review gaps."),
) -> None:
    _placeholder(
        "muni run all "
        f"--city {city} --years {years} --name {name} --state {state} "
        f"--municipal-url {municipal_url} --allow-review-gaps={allow_review_gaps}"
    )


@run_app.command("fiscal-health")
def run_fiscal_health(city: str = typer.Option(...), years: str = typer.Option(...)) -> None:
    _placeholder(f"muni run fiscal-health --city {city} --years {years}")


@run_app.command("discovery-only")
def run_discovery_only(city: str = typer.Option(...)) -> None:
    _placeholder(f"muni run discovery-only --city {city}")


@run_app.command("charts-only")
def run_charts_only(city: str = typer.Option(...)) -> None:
    _placeholder(f"muni run charts-only --city {city}")
