document.addEventListener('DOMContentLoaded', () => {
    const modalCrear = document.getElementById('modalCliente');
    const modalEditar = document.getElementById('modalEditarCliente');
    const formCrear = document.getElementById('formAgregarCliente');
    const formEditar = document.getElementById('formEditarCliente');

    const direccionesCrearContainer = document.getElementById('direccionesContainer');
    const direccionesEditarContainer = document.getElementById('direccionesEditarContainer');

    const btnAgregarDireccion = document.getElementById('btnAgregarDireccion');
    const btnAgregarDireccionEditar = document.getElementById('btnAgregarDireccionEditar');

    function construirUrl(baseUrl, id) {
        if (baseUrl && baseUrl.includes('0')) {
            return baseUrl.replace('0', String(id));
        }
        return '';
    }

    function crearFilaDireccion(container, valor = '') {
        const fila = document.createElement('div');
        fila.className = 'direccion-row';
        fila.innerHTML = `
            <input type="text" name="direcciones[]" class="direccion-input" placeholder="Ej: Av. Siempre Viva 123" required>
            <button type="button" class="btn-eliminar-direccion">Eliminar</button>
        `;

        const input = fila.querySelector('input');
        const btnEliminar = fila.querySelector('.btn-eliminar-direccion');
        input.value = valor;

        btnEliminar.addEventListener('click', () => {
            const totalFilas = container.querySelectorAll('.direccion-row').length;
            if (totalFilas <= 1) {
                showAppModal('Debe existir al menos una direccion.', {
                    variant: 'warning',
                    title: 'Direccion obligatoria'
                });
                return;
            }
            fila.remove();
        });

        return fila;
    }

    function resetearDirecciones(container) {
        container.innerHTML = '';
        container.appendChild(crearFilaDireccion(container));
    }

    function obtenerDireccionesDesdeContainer(container) {
        return Array.from(container.querySelectorAll('input[name="direcciones[]"]'))
            .map(input => input.value.trim())
            .filter(Boolean);
    }

    function validarCampos(nombre, telefono, direcciones) {
        if (!nombre) {
            showAppModal('El nombre del cliente es obligatorio.', {
                variant: 'warning',
                title: 'Campo obligatorio'
            });
            return false;
        }

        if (!telefono) {
            showAppModal('El telefono del cliente es obligatorio.', {
                variant: 'warning',
                title: 'Campo obligatorio'
            });
            return false;
        }

        if (!direcciones.length) {
            showAppModal('Debes agregar al menos una direccion.', {
                variant: 'warning',
                title: 'Campo obligatorio'
            });
            return false;
        }

        return true;
    }

    window.mostrarModalCliente = () => {
        formCrear.reset();
        resetearDirecciones(direccionesCrearContainer);
        modalCrear.style.display = 'block';
    };

    window.cerrarModalCliente = () => {
        modalCrear.style.display = 'none';
    };

    window.abrirModalEditarCliente = (clienteId) => {
        const id = String(clienteId);
        const nombre = document.getElementById(`nombre-cliente-${id}`)?.textContent.trim() || '';
        const telefono = document.getElementById(`telefono-cliente-${id}`)?.textContent.trim() || '';
        const listaDirecciones = document.getElementById(`direcciones-cliente-${id}`);

        document.getElementById('editarClienteId').value = id;
        document.getElementById('editarNombreCliente').value = nombre;
        document.getElementById('editarTelefonoCliente').value = telefono;

        direccionesEditarContainer.innerHTML = '';
        const direcciones = listaDirecciones
            ? Array.from(listaDirecciones.querySelectorAll('li'))
                .map(li => li.textContent.trim())
                .filter(texto => texto && texto.toLowerCase() !== 'sin direcciones')
            : [];

        if (!direcciones.length) {
            direccionesEditarContainer.appendChild(crearFilaDireccion(direccionesEditarContainer));
        } else {
            direcciones.forEach(direccion => {
                direccionesEditarContainer.appendChild(crearFilaDireccion(direccionesEditarContainer, direccion));
            });
        }

        modalEditar.style.display = 'block';
    };

    window.cerrarModalEditarCliente = () => {
        modalEditar.style.display = 'none';
    };

    window.confirmarEliminarCliente = (clienteId) => {
        const id = String(clienteId);
        const nombre = document.getElementById(`nombre-cliente-${id}`)?.textContent.trim() || `#${id}`;

        showAppModal(`Se eliminara el cliente ${nombre}. Esta accion no se puede deshacer.`, {
            variant: 'warning',
            title: 'Confirmar eliminacion',
            confirmText: 'Eliminar',
            cancelText: 'Cancelar',
            onConfirm: async () => {
                try {
                    const url = construirUrl(window.eliminarClienteUrl, id);
                    const response = await fetch(url, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': window.csrfToken || '',
                        },
                    });

                    const data = await response.json();
                    if (!response.ok || !data.success) {
                        throw new Error(data.message || 'No se pudo eliminar el cliente');
                    }

                    window.location.reload();
                } catch (error) {
                    showAppModal(error.message || 'No se pudo eliminar el cliente.', {
                        variant: 'danger',
                        title: 'Error al eliminar'
                    });
                }
            }
        });
    };

    btnAgregarDireccion.addEventListener('click', () => {
        direccionesCrearContainer.appendChild(crearFilaDireccion(direccionesCrearContainer));
    });

    btnAgregarDireccionEditar.addEventListener('click', () => {
        direccionesEditarContainer.appendChild(crearFilaDireccion(direccionesEditarContainer));
    });

    formCrear.addEventListener('submit', async (event) => {
        event.preventDefault();

        const nombre = (document.getElementById('nombreCliente').value || '').trim();
        const telefono = (document.getElementById('telefonoCliente').value || '').trim();
        const direcciones = obtenerDireccionesDesdeContainer(direccionesCrearContainer);

        if (!validarCampos(nombre, telefono, direcciones)) return;

        try {
            const formData = new FormData(formCrear);
            const response = await fetch(window.crearClienteUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': window.csrfToken || '',
                },
                body: formData,
            });

            const data = await response.json();
            if (!response.ok || !data.success) {
                throw new Error(data.message || 'No se pudo guardar el cliente');
            }

            window.location.reload();
        } catch (error) {
            showAppModal(error.message || 'No se pudo guardar el cliente.', {
                variant: 'danger',
                title: 'Error al guardar'
            });
        }
    });

    formEditar.addEventListener('submit', async (event) => {
        event.preventDefault();

        const id = (document.getElementById('editarClienteId').value || '').trim();
        const nombre = (document.getElementById('editarNombreCliente').value || '').trim();
        const telefono = (document.getElementById('editarTelefonoCliente').value || '').trim();
        const direcciones = obtenerDireccionesDesdeContainer(direccionesEditarContainer);

        if (!validarCampos(nombre, telefono, direcciones)) return;

        try {
            const url = construirUrl(window.editarClienteUrl, id);
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.csrfToken || '',
                },
                body: JSON.stringify({
                    nombre,
                    telefono,
                    direcciones,
                }),
            });

            const data = await response.json();
            if (!response.ok || !data.success) {
                throw new Error(data.message || 'No se pudo editar el cliente');
            }

            window.location.reload();
        } catch (error) {
            showAppModal(error.message || 'No se pudo editar el cliente.', {
                variant: 'danger',
                title: 'Error al editar'
            });
        }
    });

    window.addEventListener('click', (event) => {
        if (event.target === modalCrear) {
            window.cerrarModalCliente();
        }
        if (event.target === modalEditar) {
            window.cerrarModalEditarCliente();
        }
    });

    resetearDirecciones(direccionesCrearContainer);
    resetearDirecciones(direccionesEditarContainer);
});
