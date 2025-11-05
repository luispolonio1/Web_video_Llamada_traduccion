import json
from pathlib import Path
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.conf import settings

from apps.traduccion_senas.infraestructura.repos_fs import sign_index
from apps.traduccion_senas.aplicacion.casos_uso import construir_playlist

@require_POST
def upload_audio(request):
    """
    Recibe audio/webm + texto reconocido opcional
    Devuelve: { ok: bool, playlist: [{label,url}, ...] }
    """
    audio = request.FILES.get('audio')
    recognized = (request.POST.get('recognized') or '').strip()

    if not audio:
        return HttpResponseBadRequest('Falta audio')

    # Guardado opcional para depurar
    media_dir = Path(settings.MEDIA_ROOT) / 'audios'
    media_dir.mkdir(parents=True, exist_ok=True)
    (media_dir / audio.name).write_bytes(audio.read())

    playlist = construir_playlist(recognized, sign_index())
    return JsonResponse({'ok': True, 'playlist': playlist})

@require_POST
def live_enqueue(request):
    """
    Recibe JSON: {recognized: "..."} o POST normal con recognized
    Devuelve: { ok: bool, playlist: [...] } o error si vacío
    """
    try:
        if request.content_type and 'application/json' in request.content_type:
            data = json.loads(request.body.decode('utf-8') or '{}')
            recognized = (data.get('recognized') or '').strip()
        else:
            recognized = (request.POST.get('recognized') or '').strip()
    except Exception:
        recognized = (request.POST.get('recognized') or '').strip()

    playlist = construir_playlist(recognized, sign_index())
    if playlist:
        return JsonResponse({'ok': True, 'playlist': playlist})
    return JsonResponse({'ok': False, 'error': 'Sin coincidencias'})
