from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.models.rca import IncidentContext, RCAResponse


@dataclass
class ProviderResult:
    response: RCAResponse
    prompt_tokens: int = 0
    completion_tokens: int = 0
    fallback_used: bool = False


class AIProvider(ABC):
    name: str
    model: str

    @abstractmethod
    async def generate_rca(self, context: IncidentContext, prompt: str) -> ProviderResult:
        raise NotImplementedError
