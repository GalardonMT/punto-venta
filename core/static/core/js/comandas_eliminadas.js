function cerrarModalDetalle() {
    document.getElementById('modalDetalleEliminada').style.display = 'none';
}

function cerrarModalAdmin() {
    document.getElementById('modalVerificacionAdmin').style.display = 'none';
    document.getElementById('formVerificacionAdmin').reset();
}

async function verificarAdmin(event) {
    event.preventDefault();
    const usuario = document.getElementById('adminUsuario').value;
    const password = document.getElementById('adminPass').value;

    try {
        const response = await fetch(window.eliminarComandasUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.csrfToken,
            },
            body: JSON.stringify({ username: usuario, password: password })
        });

        const data = await response.json();
        if (data.success) {
            alert('Comandas eliminadas correctamente.');
            location.reload();
        } else {
            alert(data.error || 'Usuario o contraseña incorrectos.');
        }
    } catch (error) {
        alert('Error al verificar administrador.');
    }

    cerrarModalAdmin();
}

window.addEventListener('DOMContentLoaded', () => {
    const burbujas = document.querySelectorAll('.burbuja-eliminada');
    burbujas.forEach(burbuja => {
        burbuja.addEventListener('click', () => {
            document.getElementById('detalleId').textContent = burbuja.dataset.id || '';
            document.getElementById('detalleCliente').textContent = burbuja.dataset.cliente || 'N/A';
            document.getElementById('detalleTotal').textContent = burbuja.dataset.total || '0';
            document.getElementById('detalleMotivo').textContent = burbuja.dataset.motivo || '---';
            document.getElementById('detalleEmpleado').textContent = burbuja.dataset.empleado || '---';
            document.getElementById('detalleFecha').textContent = burbuja.dataset.fecha || '';

            document.getElementById('modalDetalleEliminada').style.display = 'flex';
        });
    });

    const btnEliminarTodas = document.getElementById('btnEliminarTodas');
    const modalAdmin = document.getElementById('modalVerificacionAdmin');

    btnEliminarTodas.addEventListener('click', () => {
        modalAdmin.style.display = 'flex';
    });
});
