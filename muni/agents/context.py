from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from muni.cities.schemas import CityProfile
from muni.config import Settings


@dataclass(frozen=True)
class AgentContext:
    city_slug: str
    years: Optional[str]
    run_id: str
    settings: Settings
    city_profile: CityProfile
    database_url: str
    artifact_dir: Path
    allow_review_gaps: bool = False

