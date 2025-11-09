async function gestionarSolicitud(solicitud_id, accion) {
    const url = accion === "aceptar" 
        ? `/Amigos/aceptar_amigos/${solicitud_id}/` 
        : `/Amigos/rechazar_amigos/${solicitud_id}/`;
    console.log(url);
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "X-Requested-With": "XMLHttpRequest"
            }
        });

        const data = await response.json();
        console.log('Respuesta del servidor:', data);

        if (response.ok) {
            Swal.fire({
                icon: 'success',
                title: data.message,
                timer: 1500,
                showConfirmButton: false
            });
            
            // 🔧 Buscar y eliminar el elemento correcto
            const elemento = document.querySelector(`button[data-id="${solicitud_id}"]`);
            if (elemento) {
                const li = elemento.closest('li');
                li.remove();
                
                // Actualizar contador
                const listaSolicitudes = document.getElementById("SolicitudesPorAceptar");
                const solicitudesRestantes = listaSolicitudes.querySelectorAll('li').length;
                const contadorSolicitudes = document.getElementById("contador-solicitudes");
                
                if (solicitudesRestantes === 0) {
                    contadorSolicitudes.classList.add("hidden");
                    listaSolicitudes.innerHTML = `
                        <li class="text-gray-400 p-4 text-center text-sm">
                            <i class="fa-solid fa-inbox text-3xl mb-2 block text-gray-600"></i>
                            No hay solicitudes disponibles
                        </li>`;
                } else {
                    contadorSolicitudes.textContent = solicitudesRestantes;
                }
            }
        } else {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: data.error || 'No se pudo procesar la solicitud.',
            });  
        }
    } catch (error) {
        console.error('Error en gestionarSolicitud:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Ocurrió un error inesperado: ' + error.message,
            timer: 2000,
            showConfirmButton: false
        });
    }
}

// helper para CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}