import { enviarSolicitud } from "./EnvioSolicitud.js";
window.enviarSolicitud = enviarSolicitud;
const input = document.getElementById("default-search");
const resultados = document.getElementById("resultados");

input.addEventListener("input", async () => {
    const query = input.value.trim();

    if (query.length < 1) {
        resultados.innerHTML = "";
        resultados.classList.add("hidden");
        return;
    }

    const form = document.querySelector("form");
        form.addEventListener("submit", function(e) {
            e.preventDefault();
        });


    try {
        const response = await fetch(`/Amigos/buscar_amigos/?nombre=${encodeURIComponent(query)}`);
        const data = await response.json();
        const amigos = Array.isArray(data?.amigos) ? data.amigos : [];

        if (amigos.length > 0) {
            resultados.innerHTML = amigos.map(u => `
                <div class="flex items-center justify-between px-4 py-2 hover:bg-gray-700 transition-colors duration-200 rounded-lg">
                    <span class="text-white font-medium">${u.nombre}</span>
                    <button onclick="enviarSolicitud(${u.id})" class="flex items-center gap-1 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold px-3 py-1 rounded-lg shadow">
                        <i class="fa-solid fa-user"></i>
                        <span>Agregar</span>
                    </button>
                </div>
                `).join("");
            resultados.classList.remove("hidden");
        } else {
            resultados.innerHTML = "<div class='p-2 text-gray-500'>Sin resultados</div>";
            resultados.classList.remove("hidden");
        }
    } catch (e) {
        console.error("Error en la búsqueda:", e);
    }
});

function selectUser(username) {
    input.value = username;
    resultados.classList.add("hidden");
}