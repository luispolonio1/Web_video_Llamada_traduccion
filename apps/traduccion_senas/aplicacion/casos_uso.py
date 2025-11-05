from typing import List, Dict
from .normalizacion import normaliza
from .segmentacion import segmentacion_greedy

def construir_playlist(transcript: str, index: Dict[str, str]) -> List[dict]:
    if not transcript:
        return []
    full = normaliza(transcript)
    direct = index.get(full) or index.get(full.replace(' ', ''))
    if direct:
        return [{'label': transcript.strip(), 'url': direct}]
    return segmentacion_greedy(transcript, index)
