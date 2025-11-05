import unicodedata
import re

def strip_accents(s: str) -> str:
    nfkd = unicodedata.normalize('NFKD', s or '')
    return ''.join(c for c in nfkd if not unicodedata.combining(c))

def normaliza(texto: str) -> str:
    t = strip_accents((texto or '').lower().strip())
    t = re.sub(r'[_\-]+', ' ', t)
    t = re.sub(r"[^\w\s]", "", t, flags=re.UNICODE)
    t = re.sub(r"\s+", " ", t).strip()
    return t
