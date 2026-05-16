from abc import ABC, abstractmethod

from muni.agents.context import AgentContext
from muni.agents.result import AgentResult


class BaseAgent(ABC):
    name: str
    description: str

    @abstractmethod
    def run(self, context: AgentContext) -> AgentResult:
        """Run the agent and return a structured result."""


class PlaceholderAgent(BaseAgent):
    """Base class for planned agents before their domain logic is implemented."""

    def run(self, context: AgentContext) -> AgentResult:
        return AgentResult.partial(
            agent_name=self.name,
            warnings=[f"Implementation pending: {self.description}."],
            next_actions=[f"Implement {self.__class__.__name__} domain logic."],
        )
