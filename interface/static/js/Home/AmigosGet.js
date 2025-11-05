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

document.addEventListener("DOMContentLoaded", function() {
  const btnAmigos = document.getElementById('btn-amigos');
  const submenu = document.getElementById('submenu');

  btnAmigos.addEventListener('click', async function() {
    submenu.classList.toggle('hidden'); // Mostrar/ocultar menú

    // Solo cargar si se va a mostrar
    if (!submenu.classList.contains('hidden')) {
      try {
        const csrftoken = getCookie('csrftoken');

        const response = await fetch('/Home/get/amigos_get/', {
          method: 'GET',
          headers: {
            'X-CSRFToken': csrftoken,
            'Accept': 'application/json',
          },
        });

        if (!response.ok) throw new Error('Error al obtener los amigos');

        // 👇 Aquí está el ajuste de la opción 1
        const data = await response.json();
        const amigos = data.amigos; // Extraemos la lista del objeto
        console.log('Amigos recibidos:', amigos);
        submenu.innerHTML = ''; // Limpiar lista anterior

        if (amigos.length > 0) {
          amigos.forEach(amigo => {
            const li = document.createElement('li');
            li.className = 'flex justify-between text-sm font-semibold';

            li.innerHTML = `
              ${amigo.username}
              <button
                class="call-btn bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded-lg text-xs"
                data-user="${amigo.username}"
                data-user-id="${amigo.id}"
                data-room="${amigo.room_name}">
                Llamar
              </button>
            `;

            submenu.appendChild(li);
          });
        } else {
          submenu.innerHTML = `
            <li class="text-gray-400 text-sm">No tienes amigos aún.</li>
          `;
        }

      } catch (error) {
        console.error('Error:', error);
        submenu.innerHTML = `
          <li class="text-red-500 text-sm">Error al cargar los amigos.</li>
        `;
      }
    }
  });
});