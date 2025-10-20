    const fechaElemento = document.getElementById('fecha');
    const ahora = new Date();
    const opciones = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' };
    const fechaFormateada = ahora.toLocaleDateString('es-ES', opciones);
    fechaElemento.textContent = fechaFormateada;