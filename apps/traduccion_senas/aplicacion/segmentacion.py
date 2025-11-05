from typing import List, Dict
from .normalizacion import normaliza

def segmentacion_greedy(transcript: str, index: Dict[str, str]) -> List[dict]:
    palabras = normaliza(transcript).split()
    if not palabras:
        return []

    max_len = max((len(k.split()) for k in index.keys() if ' ' in k), default=1)
    max_len = max(max_len, 5)

    salida, i = [], 0
    while i < len(palabras):
        match = False
        for L in range(min(max_len, len(palabras) - i), 0, -1):
            tokens = palabras[i:i+L]
            clave = ' '.join(tokens)
            url = index.get(clave) or index.get(clave.replace(' ', ''))
            if url:
                salida.append({'label': ' '.join(tokens), 'url': url})
                i += L
                match = True
                break
        if not match:
            i += 1
    return salida
