from dataclasses import dataclass, field
from pathlib import Path
from typing import List


VALID_AGENT_STATUSES = {"success", "partial", "failed", "blocked"}


@dataclass
class AgentResult:
    agent_name: str
    status: str
    records_created: int = 0
    records_updated: int = 0
    review_items_created: int = 0
    artifacts_created: List[Path] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    next_actions: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.status not in VALID_AGENT_STATUSES:
            raise ValueError(f"Invalid agent status: {self.status}")

    @classmethod
    def success(
        cls,
        agent_name: str,
        records_created: int = 0,
        records_updated: int = 0,
        review_items_created: int = 0,
        artifacts_created: List[Path] = None,
        warnings: List[str] = None,
        next_actions: List[str] = None,
    ) -> "AgentResult":
        return cls(
            agent_name=agent_name,
            status="success",
            records_created=records_created,
            records_updated=records_updated,
            review_items_created=review_items_created,
            artifacts_created=artifacts_created or [],
            warnings=warnings or [],
            next_actions=next_actions or [],
        )

    @classmethod
    def partial(
        cls,
        agent_name: str,
        warnings: List[str] = None,
        next_actions: List[str] = None,
    ) -> "AgentResult":
        return cls(
            agent_name=agent_name,
            status="partial",
            warnings=warnings or [],
            next_actions=next_actions or [],
        )

    @classmethod
    def blocked(
        cls,
        agent_name: str,
        errors: List[str] = None,
        next_actions: List[str] = None,
    ) -> "AgentResult":
        return cls(
            agent_name=agent_name,
            status="blocked",
            errors=errors or [],
            next_actions=next_actions or [],
        )

    @classmethod
    def failed(
        cls,
        agent_name: str,
        errors: List[str] = None,
        next_actions: List[str] = None,
    ) -> "AgentResult":
        return cls(
            agent_name=agent_name,
            status="failed",
            errors=errors or [],
            next_actions=next_actions or [],
        )

