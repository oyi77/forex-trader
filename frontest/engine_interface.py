from abc import ABC, abstractmethod
from typing import Any, Optional

class EngineInterface(ABC):
    @abstractmethod
    def run(self, config: Optional[dict] = None) -> Any:
        pass 