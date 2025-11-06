const scheme = window.location.protocol === "https:" ? "wss" : "ws";
const notifyUrl = `${scheme}://${window.location.host}/ws/notify/`;
window.notifySocket = new WebSocket(notifyUrl);
document.addEventListener("DOMContentLoaded", () => {
  console.log("🔁 Script notificaciones cargado");

  notifySocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log("🔔 Notificación recibida:", data);
    // ✅ Confirmación para quien llama
    if (data.type === "call_sent") {
      Swal.fire({
        title: "📞 Llamando...",
        text: `Esperando que ${data.to} responda`,
        icon: "info",
        showConfirmButton: false,
        allowOutsideClick: false,
        didOpen: () => {
          // Puedes agregar un tono o animación aquí si quieres
        }
      });
    }

    // 📞 Notificación de llamada entrante
    if (data.type === "incoming_call") {
      const ringtone = new Audio("/static/audio/Tono.mp3");
      ringtone.loop = true;
      ringtone.play();

      Swal.fire({
        title: "📞 Llamada entrante",
        text: `${data.from} quiere hablar contigo`,
        icon: "info",
        showCancelButton: true,
        confirmButtonText: "Aceptar",
        cancelButtonText: "Rechazar",
        allowOutsideClick: false,
        didClose: () => {
          ringtone.pause();
          ringtone.currentTime = 0;
        }
      }).then((result) => {
        ringtone.pause();
        ringtone.currentTime = 0;
        if (result.isConfirmed) {
          // Aceptar llamada
          notifySocket.send(JSON.stringify({
            type: "call_accepted",
            room_name: data.room_name,
            from: data.from,
            to: data.to
          }));
          window.location.href = `/Home/${data.room_name}/`;
        } else {
          // Rechazar llamada
          notifySocket.send(JSON.stringify({
            type: "call_rejected",
            room_name: data.room_name,
            from: data.from,
            to:data.to
          }));
        }
      });
    }

    // ✅ Llamada aceptada
    if (data.type === "call_accepted") {
      Swal.fire({
        title: "✅ Llamada aceptada",
        text: `${data.from} aceptó tu llamada`,
        icon: "success",
        timer: 2000,
        showConfirmButton: false
      });
      setTimeout(() => {
        window.location.href = `/Home/${data.room_name}/`;
      }, 2000);
    }

    // ❌ Llamada rechazada
    if (data.type === "call_rejected") {
      Swal.fire({
        title: "❌ Llamada rechazada",
        text: `${data.from} rechazó tu llamada`,
        icon: "error",
        timer: 2000,
        showConfirmButton: false
      });
    }

    // ⚠️ Error recibido desde el backend
    if (data.type === "error") {
      Swal.fire({
        title: "Error",
        text: data.detail || "Ocurrió un error en la conexión",
        icon: "error",
        timer: 3000,
        showConfirmButton: false
      });
    }
  };

  // Opcional: manejar desconexiones automáticas
  window.notifySocket.onclose = function(e) {
    console.warn("🔌 WebSocket cerrado:", e);
  };

  window.notifySocket.onerror = function(e) {
    console.error("⚠️ Error en WebSocket:", e);
  };
});
