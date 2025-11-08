// interface/static/js/AudioSignModule.js
(function () {
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return decodeURIComponent(parts.pop().split(';').shift());
  }

  /** Comentarios para no olvidar voz a señas
    si hay WebSocket (opts.ws o window.ws/window.WS/window.callWS), el texto reconocido
    se envía por WS con type="voice_to_sign", el servidor lo reenvía a la sala EXCEPTO al emisor.
    el receptor, al recibir ese evento, hace POST a liveUrl para obtener la playlist y la reproduce.
    Si NO hay WebSocket, se usa el flujo HTTP anterior (POST a liveUrl) y se reproduce localmente.
   */
  function mountAudioSignModule(container, opts) {
    if (!container) throw new Error('container requerido');

    const liveUrl   = (opts && opts.liveUrl) || "/senas/live-enqueue/";
    // intentamos hallar el WS si no viene por opts
    const ws        = (opts && opts.ws) || window.ws || window.WS || window.callWS || null;
    const csrftoken = getCookie('csrftoken');

    // ---------- UI ----------
    const root = document.createElement('div');
    root.innerHTML = `
    <div class="audio-sign-wrap" style="position:absolute; inset:0; pointer-events:none; z-index:10;">
      <!-- Botón en la parte inferior izquierda del contenedor -->
      <button id="as-live"
              class="as-btn"
              style="pointer-events:auto; position:absolute; bottom:16px; left:16px;">
        Traducción
      </button>

      <!-- Reproductor señas (overlay centrado en la parte inferior) -->
      <div id="as-video-wrap"
           style="position:absolute;left:50%; transform:translateX(-50%); pointer-events:auto; width:100%; height:100%; display:none;">
        <video id="as-video" playsinline
               style="width:100%; height:100%; object-fit:cover; display:block; border-radius:12px; background:#000; box-shadow: 0 4px 6px rgba(0,0,0,0.3);"></video>
      </div>
    </div>`;

    const style = document.createElement('style');
    style.textContent = `
      .as-btn{
        border:1px solid #e5e7eb; border-radius:999px; padding:10px 16px;
        background:#16a34a; color:#fff; cursor:pointer; font-weight:500;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        transition: all 0.2s;
      }
      .as-btn:hover{
        background:#15803d;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      }`;

    container.appendChild(style);
    container.appendChild(root);

    // ---------- refs ----------
    const $live  = root.querySelector('#as-live');
    const $video = root.querySelector('#as-video');
    const $wrap  = root.querySelector('#as-video-wrap');

    // ---------- estado ----------
    let recognition = null, isLive = false;
    let playlist = [], playIndex = 0;

    const DEFAULT_PLAYBACK_RATE = 2.5;
    const DEFAULT_MUTED = true;

    function showPlayer(show) {
      $wrap.style.display = show ? 'block' : 'none';
    }
    showPlayer(false);

    function playNext() {
      if (playIndex >= playlist.length) {
        showPlayer(false);
        return;
      }
      const item = playlist[playIndex];
      $video.muted = DEFAULT_MUTED;
      $video.playbackRate = DEFAULT_PLAYBACK_RATE;
      $video.src = item.url + `?t=${Date.now()}`;
      showPlayer(true);
      $video.play().catch(() => {});
    }
    $video.addEventListener('ended', () => { playIndex += 1; playNext(); });

    function setPlaylist(list) {
      playlist = Array.isArray(list) ? list.slice() : [];
      playIndex = 0;
      if (playlist.length) playNext();
    }

    function setupSR() {
      const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SR) return null;
      const sr = new SR();
      sr.lang = 'es-ES';
      sr.interimResults = true;
      sr.continuous = true;
      return sr;
    }

    // ----- Cliente HTTP para obtener playlist a partir de texto -----
    async function fetchPlaylistFromText(text) {
      try {
        const resp = await fetch(liveUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
          body: JSON.stringify({ recognized: text })
        });
        const data = await resp.json();
        if (data && data.ok && Array.isArray(data.playlist)) {
          return data.playlist;
        }
      } catch (_) {}
      return [];
    }

    // ----- Emisión de texto reconocido -----
    async function sendRecognized(text) {
      const cleaned = (text || '').trim();
      if (!cleaned) return;

      // Si hay WS, mandamos el texto por la sala -> servidor -> receptor
      if (ws && ws.readyState === WebSocket.OPEN) {
        try {
          ws.send(JSON.stringify({ type: "voice_to_sign", text: cleaned }));
          // ¡Ojo! El servidor NO se lo devuelve al emisor.
        } catch (_) {}
        return;
      }

      // Si no hay WS, fallback al flujo anterior (reproduce local)
      const list = await fetchPlaylistFromText(cleaned);
      if (list.length) setPlaylist(list);
    }

    // ----- Captura de voz -----
    function startLive() {
      const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SR) { return; }
      recognition = setupSR();
      if (!recognition) return;

      $live.textContent = 'Traduciendo…';
      recognition.onstart = () => { isLive = true; };
      recognition.onend   = () => { if (isLive) { recognition.start(); } };
      recognition.onresult = (ev) => {
        for (let i = ev.resultIndex; i < ev.results.length; i++) {
          const r = ev.results[i];
          if (r.isFinal) sendRecognized(r[0].transcript);
        }
      };
      recognition.start();
    }

    function stopLive() {
      isLive = false;
      $live.textContent = 'Traducción';
      if (recognition) { try { recognition.stop(); } catch (_) {} }
    }

    $live.addEventListener('click', () => { isLive ? stopLive() : startLive(); });

    // ----- Suscripción a mensajes del WebSocket (si existe) -----
    if (ws && typeof ws.addEventListener === 'function') {
      ws.addEventListener('message', async (evt) => {
        try {
          const data = JSON.parse(evt.data);

          // Caso: playlist ya construida desde el servidor (por si lo implementas así)
          if (data?.type === 'broadcast_message' && data.message?.type === 'sign_playlist') {
            const list = Array.isArray(data.message.playlist) ? data.message.playlist : [];
            if (list.length) setPlaylist(list);
            return;
          }

          // Caso: servidor reenvía SOLO al receptor el texto del emisor
          if (data?.type === 'broadcast_message' && data.message?.type === 'voice_to_sign') {
            const text = (data.message.text || '').trim();
            if (!text) return;
            const list = await fetchPlaylistFromText(text);
            if (list.length) setPlaylist(list);
            return;
          }
        } catch (_) { /* silencioso */ }
      });
    }

    // API pública del módulo
    return {
      // Permite reproducir una lista ya preconstruida por fuera (opcional)
      playRemote(list) { setPlaylist(list); },
      // Permite construir y reproducir a partir de texto por fuera (opcional)
      async playFromText(text) {
        const list = await fetchPlaylistFromText((text || '').trim());
        if (list.length) setPlaylist(list);
      },
      unmount() {
        stopLive();
        style.remove();
        root.remove();
      }
    };
  }

  window.mountAudioSignModule = mountAudioSignModule;
})();