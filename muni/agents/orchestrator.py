from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable, List, Optional, Sequence, Type
from uuid import uuid4

from muni.agents import DEFAULT_AGENT_CLASSES
from muni.agents.base import BaseAgent
from muni.agents.context import AgentContext
from muni.agents.result import AgentResult
from muni.cities.schemas import CityProfile
from muni.config import Settings, get_settings


@dataclass
class WorkflowResult:
    run_id: str
    results: List[AgentResult] = field(default_factory=list)

    @property
    def has_blockers(self) -> bool:
        return any(result.status in {"blocked", "failed"} for result in self.results)


class AgentOrchestrator:
    def __init__(self, agent_classes: Optional[Sequence[Type[BaseAgent]]] = None) -> None:
        self.agent_classes = list(agent_classes or DEFAULT_AGENT_CLASSES)

    def build_context(
        self,
        city_profile: CityProfile,
        years: Optional[str],
        settings: Optional[Settings] = None,
        allow_review_gaps: bool = False,
    ) -> AgentContext:
        settings = settings or get_settings()
        run_id = self._new_run_id(city_profile.slug)
        artifact_dir = settings.exports_dir / "runs" / run_id
        artifact_dir.mkdir(parents=True, exist_ok=True)
        return AgentContext(
            city_slug=city_profile.slug,
            years=years,
            run_id=run_id,
            settings=settings,
            city_profile=city_profile,
            database_url=settings.database_url,
            artifact_dir=artifact_dir,
            allow_review_gaps=allow_review_gaps,
        )

    def run_all(
        self,
        context: AgentContext,
        stop_on_blocked: bool = True,
    ) -> WorkflowResult:
        workflow_result = WorkflowResult(run_id=context.run_id)
        for agent in self.iter_agents():
            try:
                result = agent.run(context)
            except Exception as exc:
                result = AgentResult.failed(
                    agent_name=agent.name,
                    errors=[f"{exc.__class__.__name__}: {exc}"],
                    next_actions=[f"Inspect logs for {agent.name}."],
                )
            workflow_result.results.append(result)
            if stop_on_blocked and result.status in {"blocked", "failed"}:
                break
        return workflow_result

    def iter_agents(self) -> Iterable[BaseAgent]:
        for agent_class in self.agent_classes:
            yield agent_class()

    @staticmethod
    def _new_run_id(city_slug: str) -> str:
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"{city_slug}-{timestamp}-{uuid4().hex[:8]}"
