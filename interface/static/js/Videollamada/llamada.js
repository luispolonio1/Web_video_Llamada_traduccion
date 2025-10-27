
document.addEventListener("DOMContentLoaded", () => {

  window.toggleBtn  = document.getElementById("toggleProcessing");
  window.localVideo = document.getElementById("video-local");
  window.remoteVideo = document.getElementById("video-remoto");

  // Manejador del botón "Llamar"
  document.querySelectorAll(".call-btn").forEach(btn => {
    btn.addEventListener("click", async () => {
      const roomName = btn.dataset.room;
      iniciarLlamada(roomName);
    });
  });

  async function iniciarLlamada(roomName) {
    document.getElementById('Botones').classList.remove('hidden');
    console.log(`📞 Iniciando llamada a la sala: ${roomName}`);

    const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
    const wsUrl = `${wsScheme}://${window.location.host}/ws/call/${roomName}/`;
    window.ws = new WebSocket(wsUrl);

    ws.id = Math.random().toString(36).substring(2, 10);
    let localStream;
    const pc = new RTCPeerConnection({
      iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
    });

    // Mostrar video remoto
    pc.ontrack = event => {
      if (event.streams && event.streams[0]) {
        remoteVideo.srcObject = event.streams[0];
      }
    };

    // Estado ICE
    pc.oniceconnectionstatechange = () => {
      console.log("ICE:", pc.iceConnectionState);
      if (["disconnected", "failed", "closed"].includes(pc.iceConnectionState)) {
        remoteVideo.srcObject = null;
      }
    };

    // Enviar ICE
    pc.onicecandidate = event => {
      if (event.candidate) {
        ws.send(JSON.stringify({ "ice": event.candidate, "from": ws.id }));
      }
    };

    // Conectar cámara y micrófono
    try {
      localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      localVideo.srcObject = localStream;
      localStream.getTracks().forEach(track => pc.addTrack(track, localStream));
      initializeAI().then(() => {
        toggleBtn.disabled = false;
      });
      
    } catch (err) {
      console.error("Error al acceder a cámara/micrófono:", err);
      swal.fire("Error", "No se pudo acceder a la cámara o micrófono", "error");
      return;
    }

    // Crear oferta
    async function makeCall() {
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      ws.send(JSON.stringify({ "offer": offer, "from": ws.id }));
    }

    // Recepción de mensajes del socket
    ws.onmessage = async (event) => {
      const data = JSON.parse(event.data);
      if (data.from && data.from === ws.id) return;

      if (data.joined) {
        await makeCall();
        return;
      }

      if (data.offer) {
        await pc.setRemoteDescription(new RTCSessionDescription(data.offer));
        const answer = await pc.createAnswer();
        await pc.setLocalDescription(answer);
        ws.send(JSON.stringify({ "answer": answer, "from": ws.id }));
        return;
      }

      if (data.answer) {
        await pc.setRemoteDescription(new RTCSessionDescription(data.answer));
        return;
      }

      if (data.ice) {
        try {
          await pc.addIceCandidate(new RTCIceCandidate(data.ice));
        } catch (e) {
          console.error("Error agregando ICE:", e);
        }
        return;
      }

      // Opcional: mensajes broadcast (predicción, traducción, etc.)
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

      if (data.type === 'broadcast_message' && data.message?.type === 'prediccion') {
        const p = data.message;
        // Predicciones remotas (de otors usuaioros)

        // TTS - Reproducir la predicción recibida
        console.log("Predicción recibida:", p.text);
        document.getElementById("subtitle_remote").innerText = p.text;
        document.getElementById("subtitle_remote").classList.remove("hidden");
        speak(p.text);

        setTimeout(hideSubtitles, 5000);
      }


      if (data.kind === "ack") {
        console.log("Traducción:", data.traduccion);
        document.getElementById("subtitle_local").innerText = data.traduccion;
        document.getElementById("subtitle_local").classList.remove("hidden");
        speak(data.traduccion);

        setTimeout(hideSubtitles, 5000);
      }
    };

    ws.onopen = () => console.log("✅ WebSocket conectado");
    ws.onclose = () => console.log("🔌 WebSocket cerrado");
    ws.onerror = (e) => console.error("❗ Error en WebSocket:", e);
  }




});
