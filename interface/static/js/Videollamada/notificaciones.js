document.addEventListener("DOMContentLoaded", () => {
  // Crear conexión global de notificaciones
  const scheme = window.location.protocol === "https:" ? "wss" : "ws";
  const notifyUrl = `${scheme}://${window.location.host}/ws/notify/`; // ejemplo de ruta
  window.notifySocket = new WebSocket(notifyUrl);

  // Manejador de mensajes entrantes (llamada, aceptar, rechazar)
  notifySocket.onmessage = function(e) {
    const data = JSON.parse(e.data);

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
          notifySocket.send(JSON.stringify({
            type: "call_accepted",
            room_name: data.room_name,
            from: data.from
          }));
          // redirigir a la sala para iniciar la llamada real
          window.location.href = `/Home/${data.room_name}/`;
        } else {
          notifySocket.send(JSON.stringify({
            type: "call_rejected",
            room_name: data.room_name,
            from: data.from
          }));
        }
      });
    }

    if (data.type === "call_accepted") {
      Swal.fire({
        title: "✅ Llamada aceptada",
        text: `${data.from} aceptó tu llamada`,
        icon: "success",
        timer: 2000,
        showConfirmButton: false
      });
      window.location.href = `/Home/${data.room_name}/`;
    }

    if (data.type === "call_rejected") {
      Swal.fire({
        title: "❌ Llamada rechazada",
        text: `${data.from} rechazó tu llamada`,
        icon: "error",
        timer: 2000,
        showConfirmButton: false
      });
    }
  };
});