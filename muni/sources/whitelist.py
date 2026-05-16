from pathlib import Path
from typing import Iterable, List, Optional
from urllib.parse import urlparse

from muni.config import Settings, get_settings, load_yaml


class DomainWhitelistError(ValueError):
    pass


def load_allowed_domains(settings: Optional[Settings] = None) -> List[str]:
    settings = settings or get_settings()
    config_path: Path = settings.config_dir / "domains.yaml"
    data = load_yaml(config_path)
    rules = data.get("allowed_domains", [])
    return [str(rule).strip().lower() for rule in rules if str(rule).strip()]


def host_from_url(url: str) -> str:
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise DomainWhitelistError("Source URL must be an absolute HTTP or HTTPS URL.")
    return parsed.hostname.lower() if parsed.hostname else ""


def is_allowed_host(host: str, allowed_domains: Iterable[str]) -> bool:
    normalized_host = host.strip().lower().rstrip(".")
    for rule in allowed_domains:
        normalized_rule = rule.strip().lower().rstrip(".")
        if not normalized_rule:
            continue
        if normalized_rule.startswith("."):
            suffix = normalized_rule[1:]
            if normalized_host == suffix or normalized_host.endswith(normalized_rule):
                return True
        elif normalized_host == normalized_rule or normalized_host.endswith(f".{normalized_rule}"):
            return True
    return False


def validate_source_url(url: str, settings: Optional[Settings] = None) -> str:
    host = host_from_url(url)
    allowed_domains = load_allowed_domains(settings)
    if not is_allowed_host(host, allowed_domains):
        raise DomainWhitelistError(f"Domain is not whitelisted for primary sources: {host}")
    return url.strip()

