// interface/static/js/AudioSignModule.js
    window.DESTINATARIO = "Mario";
(function(){
  function getCookie(name){
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if(parts.length===2) return decodeURIComponent(parts.pop().split(';').shift());
  }

  function mountAudioSignModule(container, opts){
    if(!container) throw new Error('container requerido');
    const liveUrl   = (opts && opts.liveUrl)   || "/senas/live-enqueue/";
    const csrftoken = getCookie('csrftoken');


    const root = document.createElement('div');
    root.innerHTML = `
    <div class="audio-sign-wrap" style="position:absolute; inset:0; pointer-events:none;">
      <!-- Botón flotante -->
      <button id="as-live"
              class="as-btn"
              style="pointer-events:auto; position:absolute; top:12px; left:12px;">
        Traducción
      </button>

      <!-- Reproductor del video de señas -->
      <div style="position:absolute; right:12px; bottom:12px; pointer-events:auto; width:44%; height:32%;">
        <video id="as-video" playsinline
       style="width:100%; height:100%; object-fit:cover; display:block; border-radius:12px; background:#000"></video>

      </div>
    </div>`;
    const style = document.createElement('style');
    style.textContent = `
      .as-btn{
        border:1px solid #e5e7eb;
        border-radius:999px;
        padding:10px 14px;
        background:#111;
        color:#fff;
        cursor:pointer
      }`;
    container.appendChild(style);
    container.appendChild(root);

    // Referencias DOM
    const $live  = root.querySelector('#as-live');
    const $video = root.querySelector('#as-video');

    // --- Estado interno (sin textos/estatus visibles) ---
    let recognition=null, isLive=false;
    let playlist=[], playIndex=0;

    const DEFAULT_PLAYBACK_RATE = 2.5, DEFAULT_MUTED = true;

    function playNext(){
      if (playIndex >= playlist.length) return;
      const item = playlist[playIndex];
      $video.muted = DEFAULT_MUTED;
      $video.playbackRate = DEFAULT_PLAYBACK_RATE;
      $video.src = item.url + `?t=${Date.now()}`;
      $video.play().catch(()=>{});
    }
    $video.addEventListener('ended', ()=>{ playIndex+=1; playNext(); });

    function setupSR(){
      const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      if(!SR) return null;
      const sr = new SR();
      sr.lang='es-ES';
      sr.interimResults=true;
      sr.continuous=true;
      return sr;
    }

async function enqueueLive(text){
  if(!text || !text.trim()) return;
  try{
    // Enviar el texto por el socket, no al servidor con fetch
    if (window.notifySocket && window.notifySocket.readyState === WebSocket.OPEN) {
      window.notifySocket.send(JSON.stringify({
        type: 'speech',       // tipo de mensaje
        recognized: text.trim(),
        from:window.CURRENT_USER,   // quien lo envía
        to:window.DESTINATARIO     // destinatario
      }));
    }
  }catch(e){
    console.error("Error enviando texto por socket", e);
  }
}


    function startLive(){
      const SR = window.SpeechRecognition||window.webkitSpeechRecognition;
      if(!SR) { return; }
      recognition = setupSR();
      if(!recognition) return;

      recognition.onstart = ()=>{ isLive=true; };
      recognition.onend   = ()=>{ if(isLive){ recognition.start(); } };
      recognition.onresult = (ev)=>{
        for(let i=ev.resultIndex;i<ev.results.length;i++){
          const r=ev.results[i];
          if(r.isFinal) enqueueLive(r[0].transcript);
        }
      };
      recognition.start();
    }
    function stopLive(){
      isLive=false;
      if(recognition){ try{ recognition.stop(); }catch(_){ } }
    }

    $live.addEventListener('click', ()=>{
      isLive ? stopLive() : startLive();
    });

    return {
      unmount(){
        stopLive();
        style.remove();
        root.remove();
      }
    };
  }

  window.mountAudioSignModule = mountAudioSignModule;
})();
