from muni.agents.base import BaseAgent
from muni.agents.orchestrator import AgentOrchestrator
from muni.agents.result import AgentResult
from muni.cities.service import create_city_profile


class FirstAgent(BaseAgent):
    name = "first"
    description = "First test agent"

    def run(self, context):
        return AgentResult.success(agent_name=self.name, records_created=1)


class BlockedAgent(BaseAgent):
    name = "blocked"
    description = "Blocked test agent"

    def run(self, context):
        return AgentResult.blocked(agent_name=self.name, errors=["blocked for test"])


class NeverReachedAgent(BaseAgent):
    name = "never_reached"
    description = "Should not run"

    def run(self, context):
        return AgentResult.success(agent_name=self.name)


def test_agent_result_rejects_invalid_status():
    try:
        AgentResult(agent_name="bad", status="unknown")
    except ValueError as exc:
        assert "Invalid agent status" in str(exc)
    else:
        raise AssertionError("AgentResult accepted an invalid status")


def test_orchestrator_runs_agents_in_order_and_stops_on_blocked(tmp_path, monkeypatch):
    import muni.config as config

    monkeypatch.setattr(config, "PROJECT_ROOT", tmp_path)
    profile = create_city_profile(slug="lucknow", name="Lucknow", state="Uttar Pradesh")

    orchestrator = AgentOrchestrator(
        agent_classes=[FirstAgent, BlockedAgent, NeverReachedAgent],
    )
    context = orchestrator.build_context(city_profile=profile, years="2022-23")
    result = orchestrator.run_all(context)

    assert [agent_result.agent_name for agent_result in result.results] == ["first", "blocked"]
    assert result.has_blockers
    assert result.results[0].records_created == 1
    assert result.results[1].errors == ["blocked for test"]

