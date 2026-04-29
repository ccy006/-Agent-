from __future__ import annotations

from abc import ABC, abstractmethod

from core.context import RunContext
from core.models import AgentResult


class BaseAgent(ABC):
    name: str = "BaseAgent"

    @abstractmethod
    def run(self, context: RunContext) -> AgentResult:
        raise NotImplementedError
