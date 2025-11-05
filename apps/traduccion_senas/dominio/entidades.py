from dataclasses import dataclass

@dataclass(frozen=True)
class SignClip:
    label: str
    url: str
