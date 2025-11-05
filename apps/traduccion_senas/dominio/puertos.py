from typing import Dict, Protocol, List

class SignRepositoryPort(Protocol):
    def index(self) -> Dict[str, str]:
        ...

class SegmentadorPort(Protocol):
    def segmentar(self, transcript: str, index: Dict[str, str]) -> List[dict]:
        ...
