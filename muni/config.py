from dataclasses import dataclass
import os
from pathlib import Path
from typing import Any, Dict

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    project_root: Path
    config_dir: Path
    city_config_dir: Path
    data_dir: Path
    raw_data_dir: Path
    processed_data_dir: Path
    charts_dir: Path
    exports_dir: Path
    logs_dir: Path
    database_url: str


def get_settings() -> Settings:
    project_root = PROJECT_ROOT
    return Settings(
        project_root=project_root,
        config_dir=project_root / "configs",
        city_config_dir=project_root / "configs" / "cities",
        data_dir=project_root / "data",
        raw_data_dir=project_root / "data" / "raw",
        processed_data_dir=project_root / "data" / "processed",
        charts_dir=project_root / "data" / "charts",
        exports_dir=project_root / "data" / "exports",
        logs_dir=project_root / "data" / "logs",
        database_url=os.getenv("MUNI_DATABASE_URL", f"sqlite:///{project_root / 'data' / 'muni.db'}"),
    )


def ensure_project_dirs(settings: Settings = None) -> None:
    settings = settings or get_settings()
    for path in [
        settings.config_dir,
        settings.city_config_dir,
        settings.data_dir,
        settings.raw_data_dir,
        settings.processed_data_dir,
        settings.charts_dir,
        settings.exports_dir,
        settings.logs_dir,
    ]:
        path.mkdir(parents=True, exist_ok=True)


def load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping in {path}")
    return data


def write_yaml_if_missing(path: Path, data: Dict[str, Any]) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False)
    return True


def write_yaml(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False)


def initialize_default_configs(settings: Settings = None) -> Dict[str, bool]:
    settings = settings or get_settings()
    ensure_project_dirs(settings)
    created = {
        "domains": write_yaml_if_missing(
            settings.config_dir / "domains.yaml",
            {
                "allowed_domains": [
                    ".gov.in",
                    ".nic.in",
                    "cag.gov.in",
                    "mohua.gov.in",
                    "rbi.org.in",
                    "data.gov.in",
                    "censusindia.gov.in",
                    "mospi.gov.in",
                    "niti.gov.in",
                ]
            },
        ),
        "ontology": write_yaml_if_missing(
            settings.config_dir / "ontology.yaml",
            {
                "canonical_categories": [
                    "SOLID_WASTE_MANAGEMENT",
                    "ROAD_INFRASTRUCTURE",
                    "WATER_SUPPLY",
                    "SEWERAGE_DRAINAGE",
                    "STAFF_SALARIES",
                    "PENSION_LIABILITY",
                    "DEBT_SERVICING",
                    "SMART_CITY_PROJECTS",
                    "AMRUT_PROJECTS",
                    "PUBLIC_SPACES",
                    "STREET_LIGHTING",
                    "PUBLIC_HEALTH",
                ]
            },
        ),
    }
    return created
