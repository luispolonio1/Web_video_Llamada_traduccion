from pathlib import Path
from typing import Dict
from django.conf import settings
from apps.traduccion_senas.aplicacion.normalizacion import normaliza

# Tus videos .mp4
VIDEOS_DIR = (Path(settings.BASE_DIR) / 'interface' / 'static' / 'videos').resolve()

_INDEX_CACHE: Dict[str, str] | None = None

def build_index() -> Dict[str, str]:
    base_url = settings.STATIC_URL.rstrip('/') + '/videos/'
    idx: Dict[str, str] = {}
    if not VIDEOS_DIR.exists():
        return idx
    for mp4 in sorted(VIDEOS_DIR.glob('*.mp4')):
        title = mp4.stem
        norm = normaliza(title)
        url = f"{base_url}{mp4.name}"
        idx[norm] = url
        idx[norm.replace(' ', '')] = url
    return idx

def sign_index() -> Dict[str, str]:
    global _INDEX_CACHE
    if _INDEX_CACHE is None:
        _INDEX_CACHE = build_index()
    return _INDEX_CACHE
