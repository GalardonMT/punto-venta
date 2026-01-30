            function abrirModalEditar(id, username, grupoActual) {
                document.getElementById('editarUserId').value = id;
                document.getElementById('editarUsername').value = username;
                document.getElementById('editarPassword').value = '';
                document.getElementById('confirmarPassword').value = '';
                document.getElementById('editarGrupo').value = grupoActual;
                document.getElementById('modalEditarUsuario').style.display = 'block';
            }


            function cerrarModalEditar() {
                document.getElementById('modalEditarUsuario').style.display = 'none';
            }

            function enviarEdicion(event) {
                event.preventDefault();
                const id = document.getElementById('editarUserId').value;
                const username = document.getElementById('editarUsername').value.trim();
                const password = document.getElementById('editarPassword').value;
                const confirmar = document.getElementById('confirmarPassword').value;
                const grupo = document.getElementById('editarGrupo').value;

                if (!username || !password || !confirmar) {
                    showAppModal("Debe llenar todos los campos", {
                        variant: 'warning',
                        title: 'Datos incompletos'
                    });
                    return;
                }

                if (password !== confirmar) {
                    showAppModal("Las contraseñas no coinciden", {
                        variant: 'warning',
                        title: 'Contraseñas distintas'
                    });
                    return;
                }

                fetch(`/editar_usuario/${id}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCSRFToken(),
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username: username, password: password, grupo: grupo }),
                })
                .then(res => res.ok ? res.json() : Promise.reject("Error en la respuesta"))
                .then(data => {
                    if (data.success) {
                        cerrarModalEditar();
                        showAppModal("Usuario actualizado correctamente", {
                            variant: 'success',
                            title: 'Usuario actualizado',
                            onConfirm: () => location.reload()
                        });
                    } else {
                        showAppModal("Error: " + (data.error || "No se pudo actualizar"), {
                            variant: 'danger',
                            title: 'Error al actualizar'
                        });
                    }
                })
                .catch(error => showAppModal("Error al actualizar usuario: " + error, {
                    variant: 'danger',
                    title: 'Error al actualizar'
                }));
            }

            function getCSRFToken() {
                const cookies = document.cookie.split(';');
                for (let cookie of cookies) {
                    const [name, value] = cookie.trim().split('=');
                    if (name === 'csrftoken') return decodeURIComponent(value);
                }
                return '';
            }
            function mostrarDetalleUsuario(userId, userName) {
                fetch(`/api/comandas/${userId}/`)
                .then(response => response.json())
                .then(data => {
                    const comandasHtml = data.comandas.length === 0
                        ? '<p>No hay comandas registradas para hoy.</p>'
                        : data.comandas.map(c => `
                            <div class="comanda-burbuja estado-${c.estado === 'abierta' ? 'abierta' : 'cerrada'}">
                                <span class="estado-badge ${c.estado === 'abierta' ? 'abierta' : 'cerrada'}">
                                    ${c.estado === 'abierta' ? 'Abierta' : 'Cerrada'}
                                </span>
                                <h4>Cliente: ${c.nombre_cliente}</h4>
                                <p><strong>Fecha:</strong> ${c.fecha}</p>
                                <p><strong>Total:</strong> $${c.total}</p>
                            </div>
                        `).join('');

                    document.getElementById('contenido-detalle').innerHTML = `
                        <h3>Detalles de ${userName}</h3>
                        <p><strong>Último login:</strong> ${data.last_login}</p>
                        <p><strong>Comandas de hoy:</strong> ${data.cantidad_hoy}</p>
                        <p><strong>Total vendido hoy:</strong> $${data.total_vendido_hoy}</p>
                        <hr>
                        <div class="burbujas-container">
                            ${comandasHtml}
                        </div>
                    `;
                    document.getElementById('modalDetalleUsuario').style.display = 'block';
                })
                .catch(error => {
                    console.error('Error al obtener comandas del usuario:', error);
                });
            }

            function cerrarModalDetalle() {
                document.getElementById('modalDetalleUsuario').style.display = 'none';
            }

            function cambiarEstadoUsuario(userId, activar) {
                fetch(`/api/cambiar_estado_usuario/${userId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCSRFToken(),
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ activar: activar })
                })
                .then(res => {
                    if (res.ok) {
                        showAppModal("Estado actualizado correctamente", {
                            variant: 'success',
                            title: 'Estado actualizado',
                            onConfirm: () => location.reload()
                        });
                    } else {
                        showAppModal("Error al actualizar estado", {
                            variant: 'danger',
                            title: 'Error al actualizar'
                        });
                    }
                });
            }

            function getCSRFToken() {
                const cookies = document.cookie.split(';');
                for (let cookie of cookies) {
                    const [name, value] = cookie.trim().split('=');
                    if (name === 'csrftoken') return decodeURIComponent(value);
                }
                return '';
            }
            document.addEventListener('DOMContentLoaded', function() {
                document.getElementById('modalEditarUsuario').style.display = 'none';
            });

            let usuarioAEliminar = null;

            function confirmarEliminarUsuario(userId, username) {
                usuarioAEliminar = userId;
                document.getElementById("nombreEliminar").textContent = username;
                document.getElementById("modalConfirmarEliminar").style.display = "block";
            }

            function cerrarModalEliminar() {
                usuarioAEliminar = null;
                document.getElementById("modalConfirmarEliminar").style.display = "none";
            }

            function eliminarUsuarioConfirmado() {
                if (!usuarioAEliminar) return;

                fetch(`/eliminar_usuario/${usuarioAEliminar}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCSRFToken(),
                        'Content-Type': 'application/json'
                    }
                })
                .then(res => {
                    if (res.ok) {
                        showAppModal("Usuario eliminado correctamente", {
                            variant: 'success',
                            title: 'Usuario eliminado',
                            onConfirm: () => location.reload()
                        });
                    } else {
                        showAppModal("Error al eliminar el usuario", {
                            variant: 'danger',
                            title: 'Error al eliminar'
                        });
                    }
                })
                .catch(error => {
                    showAppModal("Error: " + error, {
                        variant: 'danger',
                        title: 'Error al eliminar'
                    });
                })
                .finally(() => {
                    cerrarModalEliminar();
                });
            }

            let usuarioEstadoId = null;
            let activarUsuario = null;

            function confirmarCambioEstado(userId, username, activar) {
                usuarioEstadoId = userId;
                activarUsuario = activar;
                const accion = activar ? 'activar' : 'desactivar';
                document.getElementById("textoConfirmacionEstado").textContent =
                    `¿Estás seguro que deseas ${accion} al usuario "${username}"?`;
                document.getElementById("modalConfirmarEstado").style.display = "block";
            }

            function cerrarModalEstado() {
                usuarioEstadoId = null;
                activarUsuario = null;
                document.getElementById("modalConfirmarEstado").style.display = "none";
            }

            function cambiarEstadoUsuarioConfirmado() {
                if (usuarioEstadoId === null) return;

                fetch(`/api/cambiar_estado_usuario/${usuarioEstadoId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCSRFToken(),
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ activar: activarUsuario })
                })
                .then(res => {
                    if (res.ok) {
                        showAppModal("Estado actualizado correctamente", {
                            variant: 'success',
                            title: 'Estado actualizado',
                            onConfirm: () => location.reload()
                        });
                    } else {
                        showAppModal("Error al actualizar estado", {
                            variant: 'danger',
                            title: 'Error al actualizar'
                        });
                    }
                })
                .catch(error => {
                    showAppModal("Error: " + error, {
                        variant: 'danger',
                        title: 'Error al actualizar'
                    });
                })
                .finally(() => {
                    cerrarModalEstado();
                });
            }
