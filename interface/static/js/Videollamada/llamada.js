document.addEventListener("DOMContentLoaded", () => {

  window.toggleBtn  = document.getElementById("toggleProcessing");
  window.localVideo = document.getElementById("video-local");
  window.remoteVideo = document.getElementById("video-remoto");
  const asContainer = document.getElementById("video-area");
  let asInstance = null;
  let asScriptLoaded = false;

  window.ws = null;
  window.pc = null;

  // 🧠 Detectar si hay una sala en la URL
  const currentRoom = window.location.pathname.split("/").filter(Boolean).pop();

  // 🔗 Si ya hay una sala en la URL, conectarse automáticamente (segundo usuario)
  if (currentRoom && currentRoom !== "Home") {
    console.log("👥 Entrando a la sala existente:", currentRoom);
    iniciarLlamada(currentRoom);
  }

// Delegación de eventos
if (!window._submenuListenerAttached) {
  const submenu = document.getElementById("submenu");

  submenu.addEventListener("click", async (e) => {

    if (e.target.classList.contains("call-btn")) {
      const btn = e.target;
      const newRoom = btn.getAttribute("data-room");
      const destinatario = btn.getAttribute("data-user");
      window.destinatario = destinatario;

      if (!window.notifySocket || window.notifySocket.readyState !== WebSocket.OPEN) {
        Swal.fire("Error", "No se pudo iniciar la llamada. Intenta de nuevo.", "error");
        return;
      }

      console.log("📤 Enviando call_request a:", destinatario, "Sala:", newRoom);

      window.notifySocket.send(
        JSON.stringify({
          type: "call_request",
          to: destinatario,
          room_name: newRoom,
        })
      );

      Swal.fire({
        title: "📞 Llamando...",
        text: `Esperando que ${destinatario} responda...`,
        icon: "info",
        showConfirmButton: false,
        allowOutsideClick: false,
      });
    }
  });

  // Marca para no volver a registrarlo
  window._submenuListenerAttached = true;
}

function loadAudioSignModule() {
    return new Promise((resolve, reject) => {
      if (asScriptLoaded) return resolve();
      const s = document.createElement("script");
      // Ajusta la ruta si tu STATIC_URL cambia
      s.src = "/static/js/AudioSignModule.js";
      s.onload = () => { asScriptLoaded = true; resolve(); };
      s.onerror = () => reject(new Error("No se pudo cargar AudioSignModule.js"));
      document.head.appendChild(s);
    });
  }

  async function montarAS() {
    try {
      await loadAudioSignModule();
      if (!asInstance && window.mountAudioSignModule) {
        asInstance = window.mountAudioSignModule(asContainer, {
          liveUrl: "/senas/live-enqueue/",
        });
      }
    } catch (e) {
      console.error("[AS] No se pudo montar el módulo:", e);
    }
  }

  function desmontarAS() {
    if (asInstance && typeof asInstance.unmount === "function") {
      try { asInstance.unmount(); } catch (_) {}
    }
    asInstance = null;
  }




  // 🎥 Función principal de conexión WebRTC
  async function iniciarLlamada(roomName) {
    document.getElementById('Botones')?.classList.remove('hidden');
    montarAS()
    console.log(`📞 Iniciando llamada en la sala: ${roomName}`);

    const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
    const wsUrl = `${wsScheme}://${window.location.host}/ws/call/${roomName}/`;
    window.ws = new WebSocket(wsUrl);
    window.ws.id = Math.random().toString(36).substring(2, 10);

    window.pc = new RTCPeerConnection({
      iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
    });

    // 🎬 Mostrar video remoto
    pc.ontrack = event => {
      if (event.streams && event.streams[0]) {
        remoteVideo.srcObject = event.streams[0];

      }
    };

    // 🧊 Estado ICE
    pc.oniceconnectionstatechange = () => {
      console.log("ICE:", pc.iceConnectionState);
      if (["disconnected", "failed", "closed"].includes(pc.iceConnectionState)) {
        remoteVideo.srcObject = null;
      }
    };

    // 📨 Enviar ICE al servidor
    pc.onicecandidate = event => {
      if (event.candidate) {
        ws.send(JSON.stringify({ "ice": event.candidate, "from": ws.id }));
      }
    };

    // 🎥 Acceso a cámara/micrófono
    let localStream;
    try {
      localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      localVideo.srcObject = localStream;
      localStream.getTracks().forEach(track => pc.addTrack(track, localStream));
      initializeAI?.().then(() => {
        if (toggleBtn) toggleBtn.disabled = false;
      });
    } catch (err) {
      console.error("❌ Error al acceder a cámara/micrófono:", err);
      swal.fire("Error", "No se pudo acceder a la cámara o micrófono", "error");
      return;
    }

    // Crear y enviar oferta
    async function makeCall() {
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      ws.send(JSON.stringify({ "offer": offer, "from": ws.id }));
    }

    // Manejador WebSocket
    ws.onmessage = async (event) => {
      const data = JSON.parse(event.data);
      if (data.from && data.from === ws.id) return;

      if (data.joined) {
        console.log("👥 Otro usuario se unió, creando oferta...");
        await makeCall();
        return;
      }

      if (data.offer) {
        console.log("📨 Oferta recibida, creando respuesta...");
        await pc.setRemoteDescription(new RTCSessionDescription(data.offer));
        const answer = await pc.createAnswer();
        await pc.setLocalDescription(answer);
        ws.send(JSON.stringify({ "answer": answer, "from": ws.id }));
        return;
      }

      if (data.answer) {
        console.log("✅ Respuesta recibida, estableciendo conexión...");
        await pc.setRemoteDescription(new RTCSessionDescription(data.answer));
        return;
      }

      if (data.ice) {
        try {
          await pc.addIceCandidate(new RTCIceCandidate(data.ice));
        } catch (e) {
          console.error("⚠️ Error agregando ICE:", e);
        }
        return;
      }
      
      // 🔊 Mensajes broadcast (predicciones / traducciones)
      if (data.type === 'broadcast_message' && data.message?.type === 'prediccion') {
        const p = data.message;

        console.log("🗣️ Predicción recibida:", p.text);
        let color;
        if (p.user === window.CURRENT_USER) {
          color = "green";
        } else{
          color = "orange";
        }
        agregarMensaje(p.user, p.text, color);
        speak(p.text);
      }

      if (data.type === 'broadcast_message' && data.message?.type === 'voice_to_sign') {
          const p = data.message;
          console.log("✋ Texto para traducción a señas:", p.text);
          let color = (p.user === window.CURRENT_USER) ? "blue" : "purple";
          agregarMensaje(p.user, p.text, color);
        }
    };

    // 🗣️ Funciones de voz/subtítulos
    function speak(text) {
      if (!text || !("speechSynthesis" in window)) return;
      window.speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(String(text));
      u.lang = "es-ES";
      u.rate = 1.6;
      u.pitch = 1.0;
      u.volume = 1.0;
      window.speechSynthesis.speak(u);
    }

    function hideSubtitles() {
      document.getElementById("subtitle_remote").innerText = "";
      document.getElementById("subtitle_local").innerText = "";
      document.getElementById("subtitle_remote").classList.add("hidden");
      document.getElementById("subtitle_local").classList.add("hidden");
    }
  }
});

// 💬 Chat
let Conversation = [];
function agregarMensaje(usuario, mensaje, color = "blue", hora = new Date()) {
  Conversation.push({ usuario, mensaje, hora });
  const chatDiv = document.getElementById("mensajes-chat");
  if (!chatDiv) return;

  const msgDiv = document.createElement("div");
  msgDiv.classList.add("bg-gray-900", "p-3", "rounded-lg","flex");
  msgDiv.innerHTML = `
    <div class="flex items-start gap-2 ">
        <div class="bg-${color}-600 rounded-full h-8 w-8 flex items-center justify-center flex-shrink-0">
            <i class="fa-solid fa-user text-white text-sm"></i>
        </div>
        <div class="flex-1">
            <p class="text-white font-semibold text-sm">${usuario===window.CURRENT_USER?'Yo':usuario}</p>
            <p class="text-gray-300 text-sm mt-1">${mensaje}</p>
            <span class="text-gray-500 text-xs">
              ${hora.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
            </span>
        </div>
    </div>
  `;
  chatDiv.appendChild(msgDiv);
  chatDiv.scrollTop = chatDiv.scrollHeight;
}

function finalizarLlamada() {
  console.log("📴 Finalizando llamada...");

  // Detener transmisión local
  if (window.localVideo?.srcObject) {
    window.localVideo.srcObject.getTracks().forEach(track => track.stop());
    window.localVideo.srcObject = null;
  }

  // Detener el video remoto
  if (window.remoteVideo) {
    window.remoteVideo.srcObject = null;
  }

  // Cerrar conexión WebRTC
  if (window.pc) {
    window.pc.ontrack = null;
    window.pc.onicecandidate = null;
    window.pc.close();
    window.pc = null;
  }

  // Cerrar WebSocket
  if (window.ws && window.ws.readyState === WebSocket.OPEN) {
    window.ws.close();
  }
  window.ws = null;

  // Desmontar módulo de señas
  if (typeof desmontarAS === "function") {
    desmontarAS();
  }

  // Ocultar botones
  document.getElementById('Botones')?.classList.add('hidden');

  Swal.fire({
    title: "Llamada finalizada",
    text: "La conexión ha sido cerrada correctamente.",
    icon: "info",
    timer: 2000,
    showConfirmButton: false,
  });
    setTimeout(() => {
           window.location.href = "/Home/";
    },1000);

  console.log("✅ Llamada cerrada correctamente");
}

// Asociar evento al botón al cargar el DOM
document.addEventListener("DOMContentLoaded", () => {
  const btnEndCall = document.getElementById("btnEndCall");
  if (btnEndCall) {
    btnEndCall.addEventListener("click", finalizarLlamada);
  }
});