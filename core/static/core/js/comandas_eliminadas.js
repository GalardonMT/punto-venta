const OWNER_PASSWORD_PLACEHOLDER = '********';

function autocompletarCredencialesAdmin() {
    if (!window.currentIsOwner) return;

    const usuarioInput = document.getElementById('adminUsuario');
    const passwordInput = document.getElementById('adminPass');

    if (usuarioInput && !usuarioInput.value) {
        usuarioInput.value = window.currentUsername || '';
    }

    if (passwordInput && !passwordInput.value) {
        passwordInput.value = OWNER_PASSWORD_PLACEHOLDER;
    }
}

function normalizarCredencialesAdmin(usuario, password) {
    let normalizedUsuario = (usuario || '').trim();
    let normalizedPassword = password || '';

    if (window.currentIsOwner && normalizedPassword === OWNER_PASSWORD_PLACEHOLDER) {
        normalizedPassword = '';
    }

    if (window.currentIsOwner && !normalizedUsuario && !normalizedPassword) {
        normalizedUsuario = window.currentUsername || '';
    }

    return {
        usuario: normalizedUsuario,
        password: normalizedPassword,
    };
}

function cerrarModalDetalle() {
    document.getElementById('modalDetalleEliminada').style.display = 'none';
}

function cerrarModalAdmin() {
    document.getElementById('modalVerificacionAdmin').style.display = 'none';
    document.getElementById('formVerificacionAdmin').reset();
}

async function verificarAdmin(event) {
    event.preventDefault();
    const usuarioInput = document.getElementById('adminUsuario');
    const passwordInput = document.getElementById('adminPass');
    const credentials = normalizarCredencialesAdmin(
        usuarioInput ? usuarioInput.value : '',
        passwordInput ? passwordInput.value : ''
    );
    const usuario = credentials.usuario;
    const password = credentials.password;

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
            showAppModal('Comandas eliminadas correctamente.', {
                variant: 'success',
                title: 'Acción completada',
                onConfirm: () => location.reload()
            });
        } else {
            showAppModal(data.error || 'Usuario o contraseña incorrectos.', {
                variant: 'danger',
                title: 'Verificación fallida'
            });
        }
    } catch (error) {
        showAppModal('Error al verificar administrador.', {
            variant: 'danger',
            title: 'Error de verificación'
        });
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
        autocompletarCredencialesAdmin();
        modalAdmin.style.display = 'flex';
    });
});
