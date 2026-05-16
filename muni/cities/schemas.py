from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class OfficialSource:
    url: str
    type: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OfficialSource":
        return cls(url=str(data["url"]), type=str(data["type"]))

    def to_dict(self) -> Dict[str, str]:
        return {"url": self.url, "type": self.type}


@dataclass
class CityProfile:
    slug: str
    name: str
    state: str
    country: str = "India"
    fiscal_year_format: str = "april_march"
    primary_language: Optional[str] = None
    secondary_language: Optional[str] = None
    official_sources: List[OfficialSource] = field(default_factory=list)
    known_agencies: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CityProfile":
        return cls(
            slug=str(data["slug"]),
            name=str(data["name"]),
            state=str(data["state"]),
            country=str(data.get("country", "India")),
            fiscal_year_format=str(data.get("fiscal_year_format", "april_march")),
            primary_language=data.get("primary_language"),
            secondary_language=data.get("secondary_language"),
            official_sources=[
                OfficialSource.from_dict(source) for source in data.get("official_sources", [])
            ],
            known_agencies=[str(agency) for agency in data.get("known_agencies", [])],
        )

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "slug": self.slug,
            "name": self.name,
            "state": self.state,
            "country": self.country,
            "fiscal_year_format": self.fiscal_year_format,
            "official_sources": [source.to_dict() for source in self.official_sources],
            "known_agencies": self.known_agencies,
        }
        if self.primary_language:
            data["primary_language"] = self.primary_language
        if self.secondary_language:
            data["secondary_language"] = self.secondary_language
        return data

