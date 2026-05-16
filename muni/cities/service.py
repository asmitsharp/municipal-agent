import re
from pathlib import Path
from typing import List, Optional

from muni.cities.schemas import CityProfile, OfficialSource
from muni.config import Settings, get_settings, load_yaml, write_yaml


_SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


class CityProfileError(ValueError):
    pass


def validate_slug(slug: str) -> str:
    normalized = slug.strip().lower()
    if not _SLUG_PATTERN.match(normalized):
        raise CityProfileError(
            "City slug must start with a lowercase letter or number and contain only "
            "lowercase letters, numbers, hyphens, or underscores."
        )
    return normalized


def city_profile_path(slug: str, settings: Optional[Settings] = None) -> Path:
    settings = settings or get_settings()
    return settings.city_config_dir / f"{validate_slug(slug)}.yaml"


def city_exists(slug: str, settings: Optional[Settings] = None) -> bool:
    return city_profile_path(slug, settings).exists()


def create_city_profile(
    slug: str,
    name: str,
    state: str,
    country: str = "India",
    fiscal_year_format: str = "april_march",
    primary_language: Optional[str] = None,
    secondary_language: Optional[str] = None,
    settings: Optional[Settings] = None,
    overwrite: bool = False,
) -> CityProfile:
    settings = settings or get_settings()
    normalized_slug = validate_slug(slug)
    path = city_profile_path(normalized_slug, settings)
    if path.exists() and not overwrite:
        raise CityProfileError(f"City profile already exists: {normalized_slug}")

    profile = CityProfile(
        slug=normalized_slug,
        name=name,
        state=state,
        country=country,
        fiscal_year_format=fiscal_year_format,
        primary_language=primary_language,
        secondary_language=secondary_language,
    )
    write_yaml(path, profile.to_dict())
    return profile


def load_city_profile(slug: str, settings: Optional[Settings] = None) -> CityProfile:
    path = city_profile_path(slug, settings)
    if not path.exists():
        raise CityProfileError(f"City profile not found: {validate_slug(slug)}")
    return CityProfile.from_dict(load_yaml(path))


def save_city_profile(profile: CityProfile, settings: Optional[Settings] = None) -> None:
    write_yaml(city_profile_path(profile.slug, settings), profile.to_dict())


def list_city_profiles(settings: Optional[Settings] = None) -> List[CityProfile]:
    settings = settings or get_settings()
    profiles: List[CityProfile] = []
    if not settings.city_config_dir.exists():
        return profiles
    for path in sorted(settings.city_config_dir.glob("*.yaml")):
        profiles.append(CityProfile.from_dict(load_yaml(path)))
    return profiles


def add_official_source(
    slug: str,
    url: str,
    source_type: str,
    settings: Optional[Settings] = None,
) -> CityProfile:
    profile = load_city_profile(slug, settings)
    normalized_url = url.strip()
    normalized_type = source_type.strip().lower()

    for source in profile.official_sources:
        if source.url == normalized_url and source.type == normalized_type:
            return profile

    profile.official_sources.append(OfficialSource(url=normalized_url, type=normalized_type))
    save_city_profile(profile, settings)
    return profile

