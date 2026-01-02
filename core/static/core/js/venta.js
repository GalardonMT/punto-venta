let ordenOriginalCategorias = [];
    function getCSRFToken() {
        let cookieValue = null;
        const name = 'csrftoken';
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

    document.addEventListener("DOMContentLoaded", function () {
        const inputBusqueda = document.getElementById('busquedaProducto');
        const editMetodoPago = document.getElementById('editMetodoPago');

        if (editMetodoPago) {
            editMetodoPago.addEventListener('change', mostrarCamposPagoEdicion);
        }
        
        if (inputBusqueda) {
            inputBusqueda.addEventListener('input', function () {
                const texto = this.value.toLowerCase();
                const productos = document.querySelectorAll('.burbuja-producto');

                productos.forEach(prod => {
                    const nombre = prod.textContent.toLowerCase();
                    prod.style.display = nombre.includes(texto) ? 'inline-block' : 'none';
                });
            });
        }
    });

    let productosSeleccionados = [];
    let total = 0;
    let estadoInicialNota = "";

    function abrirModal() { 
        console.log("abrirModal: Iniciando apertura de modal");
        
        const modal = document.getElementById("modalComanda");
        modal.style.display = "flex";

        // Reinicia campos básicos
        document.getElementById('cliente').value = '';
        document.getElementById('metodo_pago').value = 'efectivo';
        document.getElementById('servicio').value = 'servir';
        document.getElementById('notaComanda').value = '';
        document.getElementById("monto_efectivo").value = '';
        document.getElementById("monto_tarjeta_debito").value = '';
        document.getElementById("monto_tarjeta_credito").value = '';
        document.getElementById("monto_transferencia").value = '';

        // Oculta campos
        document.getElementById('pago_mixto_campos').style.display = 'none';

        // Reinicia productos seleccionados y total
        productosSeleccionados = [];
        total = 0;
        actualizarDetalle();

        // Limpia campo de búsqueda y dispara evento input
        const busqueda = document.getElementById('busquedaProducto');
        if (busqueda) {
            busqueda.value = '';
            busqueda.dispatchEvent(new Event('input'));
        }

        // Restaura el orden original de las categorías
        const categoriasSelector = document.getElementById('categoriasSelector');
        if (ordenOriginalCategorias.length) {
            ordenOriginalCategorias.forEach(btn => categoriasSelector.appendChild(btn));
        }

        // Selecciona "Todas" en categorías y muestra todos los productos
        document.querySelectorAll('.categoria-btn').forEach(btn => {
            btn.classList.toggle('activo', btn.dataset.categoria === 'todas');
        });
        document.querySelectorAll('.burbuja-producto').forEach(p => {
            p.style.display = 'inline-block';
        });

        // Selecciona "Todas" en categorías y muestra todos los productos
        document.querySelectorAll('.categoria-btn').forEach(btn => {
            btn.classList.toggle('activo', btn.dataset.categoria === 'todas');
        });
        document.querySelectorAll('.burbuja-producto').forEach(p => {
            p.style.display = 'inline-block';
        });

        // Reinicia el scroll horizontal de la barra de categorías
        const barraCategorias = document.getElementById('categoriasSelector');
        if (barraCategorias) barraCategorias.scrollLeft = 0;
        
        // Muestra todos los productos ocultos por filtro anterior
        document.querySelectorAll('.burbuja-producto').forEach(p => {
            p.style.display = 'inline-block';
        });

        // Reinicia fecha y hora
        const ahora = new Date();
        document.getElementById('fechaHora').textContent = ahora.toLocaleString();

        // Oculta botón eliminar comanda (comanda nueva)
        document.getElementById('botonEliminarComanda').style.display = 'none';

        // Limpia ID de comanda del modal
        document.getElementById('modalComanda').dataset.comandaId = '';

        // Reinicia scroll
        document.getElementById("contenidoScroll").scrollTop = 0;
        document.getElementById("detalle").scrollTop = 0;
        document.getElementById("productosBurbuja").scrollTop = 0;
    }

    function cerrarModal() {
        console.log('Cerrando modal de comanda');
        
        // Ocultar el modal
        document.getElementById('modalComanda').style.display = 'none';
        
        // Limpiar el ID de comanda del dataset (para indicar que no es edición)
        document.getElementById('modalComanda').dataset.comandaId = '';
        
        // Opcional: limpiar campos del formulario
        document.getElementById('cliente').value = '';
        document.getElementById('notaComanda').value = '';
        
        // Limpiar productos seleccionados y total
        productosSeleccionados = [];
        total = 0;
        actualizarDetalle();
        
        console.log('Modal cerrado correctamente');
    }

    function mostrarCamposPago() {
        const metodo = document.getElementById('metodo_pago').value;
        document.getElementById('pago_mixto_campos').style.display = metodo === 'mixto' ? 'block' : 'none';
    }


    // Actualiza la lista detalle y el total en la izquierda
    function actualizarDetalle() {
        const detalle = document.getElementById('detalle');
        detalle.innerHTML = '';
        total = 0;

        productosSeleccionados.forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = `
                <div style="display:flex; align-items:center; justify-content:space-between; gap:10px;">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <img src="${item.imagen}" alt="${item.nombre}" style="width:40px; height:40px; border-radius:5px;">
                        <div>
                            <strong>${item.nombre}</strong><br>
                            x${item.cantidad} - $${item.subtotal}
                        </div>
                    </div>
                    <button class="btn-eliminar-producto" data-id="${item.productoId}" style="color: red;">❌</button>
                </div>
            `;
            detalle.appendChild(li);
            total += item.subtotal;
        });

        document.getElementById('total').textContent = total;

        // Asigna evento a cada botón X
        document.querySelectorAll('.btn-eliminar-producto').forEach(btn => {
            btn.addEventListener('click', function () {
                const id = this.getAttribute('data-id');
                eliminarProductoDetalle(id);
            });
        });
    }


    function eliminarProductoDetalle(productoId) {
        const index = productosSeleccionados.findIndex(p => String(p.productoId) === String(productoId));

        if (index !== -1) {
            const precioUnitario = productosSeleccionados[index].subtotal / productosSeleccionados[index].cantidad;

            if (productosSeleccionados[index].cantidad > 1) {
                productosSeleccionados[index].cantidad -= 1;
                productosSeleccionados[index].subtotal = productosSeleccionados[index].cantidad * precioUnitario;
            } else {
                productosSeleccionados.splice(index, 1); // Elimina del array
            }

            actualizarDetalle();
        }
    }


    // Eventos para abrir mini modal al hacer click en burbuja producto
    document.querySelectorAll('.burbuja-producto').forEach(burbuja => {
        burbuja.addEventListener('click', () => {
            const id = burbuja.getAttribute('data-id');
            const nombre = burbuja.textContent.trim();
            const precio = parseFloat(burbuja.getAttribute('data-precio'));
            const imgSrc = burbuja.querySelector('img')?.src || '';

            // Busca si el producto ya está en la lista
            const productoExistente = productosSeleccionados.find(p => p.productoId === id);
            
            if (productoExistente) {
                // Si existe, aumenta la cantidad
                productoExistente.cantidad += 1;
                productoExistente.subtotal = productoExistente.cantidad * precio;
            } else {
                // Si no existe, lo agrega
                productosSeleccionados.push({
                    productoId: id.toString(),
                    nombre: nombre,
                    cantidad: 1,
                    subtotal: precio,
                    imagen: imgSrc
                });
            }

            actualizarDetalle();
        });
    });

    // Modificamos guardarComanda para enviar productosSeleccionados
    function guardarComanda(estado) {
        const cliente = document.getElementById('cliente').value;
        const metodoPago = document.getElementById('metodo_pago').value;
        const tipoServicio = document.getElementById('servicio').value;
        const montoEfectivoInput = document.getElementById('monto_efectivo');
        const montoTarjetaDebitoInput = document.getElementById('monto_tarjeta_debito');
        const montoTarjetaCreditoInput = document.getElementById('monto_tarjeta_credito');
        const montoTransferenciaInput = document.getElementById('monto_transferencia');
        const notaComanda = document.getElementById('notaComanda').value;
        const comandaId = document.getElementById('modalComanda').dataset.comandaId;
        const totalComanda = total;

        let montoEfectivo = parseInt(montoEfectivoInput.value) || 0;
        let montoTarjetaDebito = parseInt(montoTarjetaDebitoInput.value) || 0;
        let montoTarjetaCredito = parseInt(montoTarjetaCreditoInput.value) || 0;
        let montoTransferencia = parseInt(montoTransferenciaInput.value) || 0;

        if (!cliente || productosSeleccionados.length === 0) {
            alert("Debe ingresar el cliente y al menos un producto.");
            return;
        }

        if (metodoPago === 'mixto') {
            const suma = montoEfectivo + montoTarjetaCredito + montoTarjetaDebito + montoTransferencia;
            if (suma !== totalComanda) {
                alert(`⚠️ La suma de los pagos ($${suma}) no coincide con el total: $${totalComanda}`);
                return;
            }
        } else if (metodoPago === 'efectivo') {
            montoEfectivo = totalComanda;
            montoTarjetaDebito = 0;
            montoTarjetaCredito = 0;
            montoTransferencia = 0;
        } else if (metodoPago === 'tarjeta_debito') {
            montoTarjetaDebito = totalComanda;
            montoTarjetaCredito = 0;
            montoEfectivo = 0;
            montoTransferencia = 0;
        } else if (metodoPago === 'tarjeta_credito') {
            montoTarjetaCredito = totalComanda;
            montoTarjetaDebito = 0;
            montoEfectivo = 0;
            montoTransferencia = 0;
        } else if (metodoPago === 'transferencia') {
            montoTransferencia = totalComanda;
            montoEfectivo = 0;
            montoTarjetaDebito = 0;
            montoTarjetaCredito = 0;
        }

        const payload = {
            cliente: cliente,
            productos: productosSeleccionados,
            estado: estado,
            metodo_pago: metodoPago,
            tipo_servicio: tipoServicio,
            monto_efectivo: montoEfectivo,
            monto_tarjeta_debito: montoTarjetaDebito,
            monto_tarjeta_credito: montoTarjetaCredito,
            monto_transferencia: montoTransferencia,
            nota_comanda: notaComanda
        };

        const url = comandaId ? `/editar-comanda/${comandaId}/` : '/guardar_comanda/';
        
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(payload)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Respuesta del servidor:', data);
            
            if (data.status === 'ok') {
                console.log('Comanda guardada exitosamente');
                
                // Cerrar el modal
                cerrarModal();
                
                // Actualizar la lista de comandas
                actualizarComandas();
                
                // Mostrar mensaje de éxito opcional
                if (estado === 'cerrada') {
                    console.log('Comanda cerrada y boletas enviadas a imprimir');
                }
            } else {
                console.error('Error del servidor:', data.message);
                alert(`Error al guardar la comanda: ${data.message || 'Error desconocido'}`);
            }
        })
        .catch(error => {
            console.error('Error en la petición:', error);
            alert(`Error al conectar con el servidor: ${error.message}`);
        });
    }


    // EDITAR COMANDA

    function abrirEdicionComanda(comandaId) {
        fetch(`/comanda-detalle/${comandaId}/`)
        .then(response => response.json())
        .then(data => {
            // Abre el modal principal
            document.getElementById('modalComanda').style.display = 'flex';

            // Rellena campos
            document.getElementById('cliente').value = data.cliente || '';
            document.getElementById('metodo_pago').value = data.metodo_pago || 'efectivo';
            document.getElementById('servicio').value = data.tipo_servicio || 'servir';

            mostrarCamposPago();
            document.getElementById('monto_efectivo').value = data.monto_efectivo || '';
            document.getElementById('monto_tarjeta_debito').value = data.monto_tarjeta_debito || '';
            document.getElementById('monto_tarjeta_credito').value = data.monto_tarjeta_credito || '';
            document.getElementById('monto_transferencia').value = data.monto_transferencia || '';

            document.getElementById('notaComanda').value = data.nota_comanda || '';


            // Rellena productos
            productosSeleccionados = [];

            (data.detalles || []).forEach(item => {
                // Si no hay imagen o es null/undefined, usar imagen por defecto
                const imagenProducto = item.imagen || (window.defaultImageUrl || '/static/core/img/default.jpg');
                
                productosSeleccionados.push({
                    productoId: String(item.producto_id),
                    nombre: item.producto,
                    cantidad: item.cantidad,
                    subtotal: item.subtotal,
                    imagen: imagenProducto 
                });
            });
            actualizarDetalle();

            // Guardamos ID en un atributo para saber si es edición
            document.getElementById('modalComanda').dataset.comandaId = comandaId;
            document.getElementById('botonEliminarComanda').style.display = 'block';

            // Limpia campo de búsqueda y dispara evento input
            const busqueda = document.getElementById('busquedaProducto');
            if (busqueda) {
                busqueda.value = '';
                busqueda.dispatchEvent(new Event('input'));
            }

            // Restaura el orden original de las categorías
            const categoriasSelector = document.getElementById('categoriasSelector');
            if (ordenOriginalCategorias.length) {
                ordenOriginalCategorias.forEach(btn => categoriasSelector.appendChild(btn));
            }

            // Selecciona "Todas" en categorías y muestra todos los productos
            document.querySelectorAll('.categoria-btn').forEach(btn => {
                btn.classList.toggle('activo', btn.dataset.categoria === 'todas');
            });
            document.querySelectorAll('.burbuja-producto').forEach(p => {
                p.style.display = 'inline-block';
            });
        });
    }

    function guardarEdicionComanda(estado = null) {
        const comandaId = document.getElementById('editComandaId').textContent.trim();
        const cliente = document.getElementById('editCliente').value;
        const metodoPago = document.getElementById('editMetodoPago').value;
        const tipoServicio = document.getElementById('editTipoServicio').value;
        const montoEfectivo = document.getElementById('editMontoEfectivo').value;
        const montoTarjetaDebito = document.getElementById('editMontoTarjetaDebito').value;
        const montoTarjetaCredito = document.getElementById('editMontoTarjetaCredito').value;
        const montoTransferencia = document.getElementById('editMontoTransferencia').value;
        const notaComanda = document.getElementById('editNotaComanda').value;
        
        let productosSeleccionados = [];

        let payload = {
            cliente: cliente,
            metodo_pago: metodoPago,
            tipo_servicio: tipoServicio,
            monto_efectivo: montoEfectivo,
            monto_tarjeta_debito: montoTarjetaDebito,
            monto_tarjeta_credito: montoTarjetaCredito,
            monto_transferencia: montoTransferencia,
            nota_comanda: notaComanda,
            productos: productosSeleccionados
        };

        if (estado) payload.estado = estado;

        fetch(`/editar-comanda/${comandaId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                cerrarModalEdicion();
                actualizarComandas();
            } else {
                alert("Error al guardar cambios.");
            }
        });
    }


    function mostrarCamposPagoEdicion() {
        const metodo = document.getElementById('editMetodoPago').value;
        const camposMixtos = document.getElementById('editPagoMixtoCampos');
        camposMixtos.style.display = metodo === 'mixto' ? 'block' : 'none';
    }
    

    function cerrarModalEdicion() {
        document.getElementById('modalEditarComanda').style.display = 'none';
    }

    function eliminarComanda() {
        const id = document.getElementById('editComandaId').textContent;
        
        if (!confirm("¿Estás seguro que deseas eliminar esta comanda?")) return;

        fetch(`/eliminar-comanda/${id}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                cerrarModalEdicion();
                actualizarComandas();
            } else {
                alert("No se pudo eliminar la comanda.");
            }
        });
    }

    function actualizarComandas() {
        console.log('Actualizando lista de comandas...');
        
        fetch('/comandas-json/')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Comandas obtenidas:', data);
            
            const abiertas = document.querySelectorAll('.contenedor-burbujas')[0];
            const cerradas = document.querySelectorAll('.contenedor-burbujas')[1];

            if (!abiertas || !cerradas) {
                console.error('No se encontraron los contenedores de comandas');
                return;
            }

            abiertas.innerHTML = '';
            cerradas.innerHTML = '';

            data.comandas.forEach(comanda => {
                const burbuja = document.createElement('div');
                burbuja.className = 'burbuja';
                burbuja.setAttribute('data-id', comanda.id);

                burbuja.innerHTML = `
                    <div class="estado ${comanda.estado === 'cerrada' ? 'estado-pagado' : 'estado-pendiente'}">
                        ${comanda.estado === 'cerrada' ? 'Pagado' : 'Pendiente'}
                    </div>
                    <div>Cliente: ${comanda.cliente}</div>
                    <div class="numero-comanda">#${comanda.id}</div>
                `;

                if (comanda.estado === 'abierta') {
                    burbuja.onclick = () => abrirEdicionComanda(comanda.id);
                    abiertas.appendChild(burbuja);
                } else {
                    burbuja.onclick = () => abrirDetalleCerrada(comanda.id, comanda.es_historial);
                    cerradas.appendChild(burbuja);
                }
            });
            
            console.log('Lista de comandas actualizada correctamente');
        })
        .catch(error => {
            console.error('Error al actualizar comandas:', error);
        });
    }


    function activarFiltroBusqueda() {
        const input = document.getElementById('busquedaProducto');
        const productos = document.querySelectorAll('.burbuja-producto');

        input.addEventListener('input', function () {
            const texto = input.value.toLowerCase();

            productos.forEach(producto => {
                const nombre = producto.textContent.toLowerCase();
                if (nombre.includes(texto)) {
                    producto.style.display = 'inline-block';
                } else {
                    producto.style.display = 'none';
                }
            });
        });
    }
    
    function eliminarComandaDesdeModal() {
        const comandaId = document.getElementById('modalComanda').dataset.comandaId;
        if (!comandaId) return;
        
        // Oculta el modal de comanda
        cerrarModal();
        
        // Guarda el ID en el modal de eliminación y lo muestra
        const modalEliminar = document.getElementById("modalEliminarComanda");
        modalEliminar.dataset.comandaId = comandaId;
        modalEliminar.style.display = "flex";  // Usa "flex" para que se vea como el otro modal
    }
    
    function verificarYEliminarComanda() {
        const username = document.getElementById('adminEliminar').value;
        const password = document.getElementById('passEliminar').value;
        const motivo = document.getElementById('motivoEliminar').value;
        const comandaId = document.getElementById('modalEliminarComanda').dataset.comandaId;

        if (!username || !password || !motivo) {
            mostrarError("Todos los campos son obligatorios.");
            return;
        }

        fetch('/verificar-y-eliminar-comanda/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                admin: username,
                pass: password,
                motivo: motivo,
                comanda_id: comandaId
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                cerrarModalEliminar();
                cerrarModal();  // Cierra el modal de comanda
                actualizarComandas();
            } else {
                mostrarError(data.error || "No se pudo eliminar.");
            }
        });
    }
    
    function mostrarModalCerrarCaja() {
        document.getElementById('modalCerrarCaja').style.display = 'block';
    }

    function cerrarModalCerrarCaja() {
        document.getElementById('modalCerrarCaja').style.display = 'none';
        document.getElementById('mensaje-error-cierre').style.display = 'none';
        document.getElementById('adminCierre').value = '';
        document.getElementById('passCierre').value = '';
    }

    function verificarYConfirmarCierre() {
        const username = document.getElementById('adminCierre').value;
        const password = document.getElementById('passCierre').value;

        fetch(window.verificarSuperusuarioUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.csrfToken
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.es_superusuario) {
                cerrarModalCerrarCaja();
                cerrarCaja(username);  // Aquí llamamos a la función que hace el cierre real
            } else {
                document.getElementById('mensaje-error-cierre').textContent = 
                    'Credenciales incorrectas o no tiene privilegios de administrador';
                document.getElementById('mensaje-error-cierre').style.display = 'block';
            }
        });
    }

    function cerrarCaja(adminUsername) {
        fetch('/cerrar-caja/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.csrfToken
            },
            body: JSON.stringify({
                admin_username: adminUsername
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                alert('Caja cerrada correctamente');
                location.reload();
            } else {
                alert('Error al cerrar caja: ' + data.message);
            }
        });
    }

    function cerrarModalEliminar() {
        document.getElementById("modalEliminarComanda").style.display = "none";
        document.getElementById("errorEliminar").style.display = "none";
        document.getElementById("adminEliminar").value = '';
        document.getElementById("passEliminar").value = '';
        document.getElementById("motivoEliminar").value = '';
    }


    function mostrarError(msg) {
        const errorDiv = document.getElementById('errorEliminar');
        errorDiv.textContent = msg;
        errorDiv.style.display = 'block';
    }

    function filtrarPorCategoria(categoriaId) {
        // Cambia el botón activo
        document.querySelectorAll('.categoria-btn').forEach(btn => {
            btn.classList.toggle('activo', btn.dataset.categoria === categoriaId);
        });

        // Muestra/oculta productos
        document.querySelectorAll('.burbuja-producto').forEach(prod => {
            if (categoriaId === 'todas' || prod.dataset.categoria === categoriaId) {
                prod.style.display = 'inline-block';
            } else {
                prod.style.display = 'none';
            }
        });

        // Limpia la barra de búsqueda
        const busqueda = document.getElementById('busquedaProducto');
        if (busqueda) busqueda.value = '';
        }

        document.addEventListener("DOMContentLoaded", function () {
        const inputBusqueda = document.getElementById('busquedaProducto');
        const categoriasSelector = document.getElementById('categoriasSelector');
        const categoriaBtns = Array.from(categoriasSelector.querySelectorAll('.categoria-btn'));

        // Guarda el orden original solo una vez
        ordenOriginalCategorias = categoriaBtns.slice();

        if (inputBusqueda) {
            inputBusqueda.addEventListener('input', function () {
                const texto = this.value.toLowerCase();

                // --- FILTRO DE PRODUCTOS ---
                const productos = document.querySelectorAll('.burbuja-producto');
                productos.forEach(prod => {
                    const nombre = prod.textContent.toLowerCase();
                    prod.style.display = nombre.includes(texto) ? 'inline-block' : 'none';
                });

                // --- REORDENAR CATEGORÍAS ---
                if (texto === "") {
                    // Restaurar orden original
                    ordenOriginalCategorias.forEach(btn => categoriasSelector.appendChild(btn));
                    return;
                }

                // "Todas" siempre primero
                const todasBtn = ordenOriginalCategorias.find(btn => btn.dataset.categoria === "todas");
                if (todasBtn) categoriasSelector.appendChild(todasBtn);

                // Coincidentes primero, luego el resto
                const coincidentes = ordenOriginalCategorias.filter(btn =>
                    btn !== todasBtn && btn.textContent.toLowerCase().includes(texto)
                );
                const noCoincidentes = ordenOriginalCategorias.filter(btn =>
                    btn !== todasBtn && !btn.textContent.toLowerCase().includes(texto)
                );

                coincidentes.forEach(btn => categoriasSelector.appendChild(btn));
                noCoincidentes.forEach(btn => categoriasSelector.appendChild(btn));
            });
        }
    });

    function filtrarPorCategoria(categoriaId) {
        // Cambia el botón activo
        document.querySelectorAll('.categoria-btn').forEach(btn => {
            btn.classList.toggle('activo', btn.dataset.categoria === categoriaId);
        });

        // Muestra/oculta productos
        document.querySelectorAll('.burbuja-producto').forEach(prod => {
            if (categoriaId === 'todas' || prod.dataset.categoria === categoriaId) {
                prod.style.display = 'inline-block';
            } else {
                prod.style.display = 'none';
            }
        });

        // Limpia la barra de búsqueda
        const busqueda = document.getElementById('busquedaProducto');
        if (busqueda) busqueda.value = '';
    }

    function abrirDetalleCerrada(comandaId, esHistorial) {
        const url = esHistorial
            ? `/historial-comanda-detalle/${comandaId}/`
            : `/comanda-detalle/${comandaId}/`;

        fetch(url)
        .then(response => response.json())
        .then(data => {
            // Traducir método de pago
            let metodoPago = data.metodo_pago;
            switch (metodoPago) {
                case 'efectivo': metodoPago = 'Efectivo'; break;
                case 'tarjeta_debito': metodoPago = 'Tarjeta Débito'; break;
                case 'tarjeta_credito': metodoPago = 'Tarjeta Crédito'; break;
                case 'transferencia': metodoPago = 'Transferencia'; break;
                case 'mixto': metodoPago = 'Mixto'; break;
                default: metodoPago = metodoPago || '';
            }

            let html = `
                <div class="sticky-header-comanda">
                    <h2 class="content-header">🧾 Comanda #${data.id}</h2>
                    <span class="cerrar" onclick="cerrarModalDetalleCerrada()">&times;</span>
                </div>

                <div class="scroll-detalle">
                    <div class="contenido-formulario-comanda">
                        <div class="form-group">
                            <label>Cliente:</label>
                            <div>${data.cliente || 'No asignado'}</div>
                        </div>

                        <div class="form-group">
                            <label>Tipo de Servicio:</label>
                            <div>${data.tipo_servicio}</div>
                        </div>

                        <div class="form-group">
                            <label>Método de Pago:</label>
                            <div>${metodoPago}</div>
                        </div>

                        <div class="form-group">
                            <label>Total:</label>
                            <div><strong>$${data.total}</strong></div>
                        </div>

                        ${data.nota_comanda ? `
                        <div class="form-group">
                            <label class="label-nota">Nota:</label>
                            <div class="textarea-nota" style="background:#f9f9f9; border:none;">
                                ${data.nota_comanda}
                            </div>
                        </div>` : ''}

                        <div class="form-group">
                            <label>Productos:</label>
                            <table style="width:100%; border-collapse:collapse; font-size: 15px;">
                                <thead style="background-color: #f1f1f1;">
                                    <tr>
                                        <th style="text-align:left; padding: 8px;">Producto</th>
                                        <th style="text-align:center; padding: 8px;">Cantidad</th>
                                        <th style="text-align:right; padding: 8px;">Subtotal</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${(data.detalles || []).map(item => `
                                        <tr style="border-bottom: 1px solid #ddd;">
                                            <td style="padding: 6px 8px;">${item.producto || ''}</td>
                                            <td style="padding: 6px 8px; text-align:center;">${item.cantidad}</td>
                                            <td style="padding: 6px 8px; text-align:right;">$${item.subtotal}</td>
                                        </tr>`).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <div class="footer-modal-comanda">
                    <div class="grupo-botones">
                        <button class="boton-modal verde" onclick="imprimirComandaDesdeModal('cliente')">🖨️ Imprimir Cliente</button>
                        <button class="boton-modal verde" onclick="imprimirComandaDesdeModal('cocina')">🖨️ Imprimir Cocina</button>
                        <button class="boton-modal rojo" onclick="reabrirComanda(${data.id})">🧾 Reabrir Comanda</button>
                    </div>
                </div>
            `;

            const contenedor = document.getElementById('detalleCerradaContenido');
            contenedor.innerHTML = html;

            // Reiniciar scroll al abrir
            const scrollable = contenedor.querySelector('.scroll-detalle');
            if (scrollable) scrollable.scrollTop = 0;

            document.getElementById('modalDetalleCerrada').style.display = 'flex';
        });
    }


    let comandaAReabrir = null;

    function reabrirComanda(comandaId) {
        comandaAReabrir = comandaId;
        document.getElementById("modalDetalleCerrada").style.display = "none";
        document.getElementById("modalSuperAdmin").style.display = "flex";
    }

    function cerrarModalSuperAdmin() {
        document.getElementById("modalSuperAdmin").style.display = "none";
        document.getElementById("usernameSuperAdmin").value = '';
        document.getElementById("passwordSuperAdmin").value = '';
    }

    function confirmarSuperadmin() {
        const username = document.getElementById("usernameSuperAdmin").value;
        const password = document.getElementById("passwordSuperAdmin").value;

        fetch("/verificar-superusuario/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({ username, password }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.es_superusuario) {
                cerrarModalSuperAdmin();

                // Verifica si se trata de impresión
                if (comandaAImprimir !== null && tipoImpresion !== null) {
                    // Imprimir la comanda ahora
                    const url = tipoImpresion === 'cocina'
                        ? `/imprimir-boleta-cocina/${comandaAImprimir}/`
                        : `/imprimir-boleta-comanda/${comandaAImprimir}/`;

                    fetch(url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCSRFToken(),
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'ok') {
                            const tipoTexto = tipoImpresion === 'cocina' ? 'boleta de cocina' : 'boleta de cliente';
                            alert(`${tipoTexto.charAt(0).toUpperCase() + tipoTexto.slice(1)} enviada a la impresora.`);
                        } else {
                            alert("Error al imprimir: " + (data.message || ''));
                        }

                        // Limpiar variables
                        comandaAImprimir = null;
                        tipoImpresion = null;
                    });

                    return;
                }

                // Si no es impresión, es reabrir comanda
                if (comandaAReabrir !== null) {
                    if (confirm("¿Estás seguro de que deseas reabrir esta comanda?")) {
                        fetch(`/reabrir-comanda/${comandaAReabrir}/`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCSRFToken(),
                            }
                        })
                        .then(response => {
                            if (response.ok) {
                                alert("Comanda reabierta correctamente.");
                                location.reload();
                            } else {
                                alert("No se pudo reabrir la comanda.");
                            }
                        });
                    }

                    comandaAReabrir = null;
                }
            } else {
                alert("Credenciales inválidas o no tiene permisos.");
            }
        })
        .catch(error => {
            console.error("Error al verificar superusuario:", error);
            alert("Error en la verificación.");
        });
    }


    function cerrarModalDetalleCerrada() {
        document.getElementById('modalDetalleCerrada').style.display = 'none';
        // Limpia el contenido y reinicia el scroll
        const detalleDiv = document.getElementById('detalleCerradaContenido');
        detalleDiv.innerHTML = '';
        detalleDiv.scrollTop = 0;
    }

    let comandaAImprimir = null;
    let tipoImpresion = null;

    function imprimirComandaDesdeModal(tipo = 'cliente') {
        const html = document.getElementById('detalleCerradaContenido').innerHTML;
        const match = html.match(/Comanda #(\d+)/);
        if (!match) {
            alert("No se pudo obtener el ID de la comanda.");
            return;
        }

        comandaAImprimir = match[1];
        tipoImpresion = tipo;

        document.getElementById("modalDetalleCerrada").style.display = "none";
        document.getElementById("modalSuperAdmin").style.display = "flex";
    }
