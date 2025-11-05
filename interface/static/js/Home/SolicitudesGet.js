document.addEventListener("DOMContentLoaded", () => {
  const btnSolicitudes = document.getElementById("btn-solicitudes");
  const listaSolicitudes = document.getElementById("SolicitudesPorAceptar");
  const contadorSolicitudes = document.getElementById("contador-solicitudes");

  // Al hacer clic en el ícono de solicitudes
  btnSolicitudes.addEventListener("click", async () => {
    listaSolicitudes.classList.toggle("hidden");

    if (!listaSolicitudes.classList.contains("hidden")) {
      try {
        const response = await fetch("get/solicitudes_amigos_get/");
        if (!response.ok) throw new Error("Error al obtener las solicitudes");

        const data = await response.json();
        const solicitudes = data.solicitudes;
        listaSolicitudes.innerHTML = ""; // limpiar anteriores

        // Actualizar contador
        if (solicitudes.length > 0) {
          contadorSolicitudes.classList.remove("hidden");
          contadorSolicitudes.textContent = solicitudes.length;
        } else {
          contadorSolicitudes.classList.add("hidden");
        }

        if (solicitudes.length > 0) {
          solicitudes.forEach(s => {
            const li = document.createElement("li");
            li.className = "border-b border-gray-700 last:border-b-0 p-3 hover:bg-gray-750";
            li.innerHTML = `
              <div class="flex items-start gap-3">
                <div class="bg-gray-600 rounded-full h-10 w-10 flex items-center justify-center flex-shrink-0">
                  <i class="fa-solid fa-user text-gray-300"></i>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-white font-medium text-sm">${s.from_user_username}</p>
                  <p class="text-gray-400 text-xs mb-2">Solicitud de amistad</p>
                  <div class="flex gap-2">
                    <button 
                      class="btn-aceptar flex-1 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium py-1.5 px-3 rounded transition-colors"
                      data-id="${s.solicitud_id}">
                      <i class="fa-solid fa-check mr-1"></i> Aceptar
                    </button>
                    <button 
                      class="btn-rechazar flex-1 bg-gray-600 hover:bg-gray-700 text-white text-xs font-medium py-1.5 px-3 rounded transition-colors"
                      data-id="${s.solicitud_id}">
                      <i class="fa-solid fa-xmark mr-1"></i> Rechazar
                    </button>
                  </div>
                </div>
              </div>
            `;
            listaSolicitudes.appendChild(li);
          });
        } else {
          listaSolicitudes.innerHTML = `
            <li class="text-gray-400 p-4 text-center text-sm">
              <i class="fa-solid fa-inbox text-3xl mb-2 block text-gray-600"></i>
              No hay solicitudes disponibles
            </li>`;
        }

      } catch (error) {
        console.error(error);
        listaSolicitudes.innerHTML = `
          <li class="text-red-500 p-4 text-center text-sm">Error al cargar solicitudes.</li>`;
      }
    }
  });

    listaSolicitudes.addEventListener("click", async (e) => {
    if (e.target.closest(".btn-aceptar")) {
      const id = e.target.closest(".btn-aceptar").dataset.id;
      await gestionarSolicitud(id, "aceptar");
    }

    if (e.target.closest(".btn-rechazar")) {
      const id = e.target.closest(".btn-rechazar").dataset.id;
      await gestionarSolicitud(id, "rechazar");
    }
  });
});