// Verificar que las variables globales estén definidas cuando se carga el script
document.addEventListener('DOMContentLoaded', function() {
    if (!window.csrfToken || !window.editarProductoUrl || !window.eliminarProductoUrl) {
        console.error('Variables globales no definidas correctamente');
        console.log('csrfToken:', window.csrfToken);
        console.log('editarProductoUrl:', window.editarProductoUrl);
        console.log('eliminarProductoUrl:', window.eliminarProductoUrl);
    }
});

const csrfToken = window.csrfToken;

        function escaparHTML(texto) {
            return texto
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }

        // Función auxiliar para construir URLs de forma más robusta
        function construirUrlEdicion(id) {
            // Intentar usar la variable global primero
            if (window.editarProductoUrl && window.editarProductoUrl.includes('/editar/')) {
                return window.editarProductoUrl.replace("0", id);
            }
            // Fallback usando la URL directa
            return `/productos/editar/${id}/`;
        }

        function construirUrlEliminacion(id) {
            // Intentar usar la variable global primero
            if (window.eliminarProductoUrl && window.eliminarProductoUrl.includes('/eliminar/')) {
                return window.eliminarProductoUrl.replace("0", id);
            }
            // Fallback usando la URL directa
            return `/productos/eliminar/${id}/`;
        }

        function activarEdicion(id) {
            console.log('=== ACTIVAR EDICIÓN ===');
            console.log('ID del producto:', id);
            console.log('Variables globales disponibles:');
            console.log('- csrfToken:', window.csrfToken);
            console.log('- editarProductoUrl:', window.editarProductoUrl);
            
            // Verificar que las variables globales estén disponibles
            if (!window.csrfToken) {
                console.error('Token CSRF no disponible');
                alert('Error: No se puede obtener el token de seguridad');
                return;
            }

            const nombre = document.getElementById(`nombre-${id}`).innerText;
            const descripcion = document.getElementById(`descripcion-${id}`).innerText;
            const precio = document.getElementById(`precio-${id}`).innerText;
            const imagenHTML = document.getElementById(`imagen-${id}`).innerHTML;

            // Obtiene la categoría actual desde una celda oculta que agregaremos
            const categoriaActual = document.getElementById(`categoria-${id}`).dataset.valor;
            const categoriaTexto = document.getElementById(`categoria-${id}`).textContent;

            // Usar la función auxiliar para construir la URL
            const formAction = construirUrlEdicion(id);
            console.log('URL de acción del formulario:', formAction);
            
            const csrf = window.csrfToken;
            const fila = document.getElementById(`row-${id}`);

            let opcionesCategoria = '';
            const parser = new DOMParser();
            const parsedHTML = parser.parseFromString(window.categoriasOpciones, 'text/html');
            const allOptions = parsedHTML.querySelectorAll('option');

            allOptions.forEach(opt => {
                const selected = opt.value === categoriaActual ? 'selected' : '';
                opcionesCategoria += `<option value="${opt.value}" ${selected}>${opt.textContent}</option>`;
            });

            // Agregar opción vacía si no hay categoría seleccionada
            if (!categoriaActual) {
                opcionesCategoria = `<option value="" selected>Sin categoría</option>` + opcionesCategoria;
            } else {
                opcionesCategoria = `<option value="">Sin categoría</option>` + opcionesCategoria;
            }

            fila.innerHTML = `
                <td>${id}</td>
                <td>
                    <div id="imagen-${id}">${imagenHTML}</div>
                    <input type="file" name="imagen" form="form-${id}">
                    <br>
                    <button type="button" onclick="marcarBorrarImagen(${id})" id="btn-borrar-imagen-${id}">Eliminar imagen</button>
                    <input type="hidden" name="borrar_imagen" id="borrar-imagen-${id}" value="0" form="form-${id}">
                </td>
                <td><input type="text" name="nombre" value="${escaparHTML(nombre)}" form="form-${id}" required></td>
                <td><input type="text" name="descripcion" value="${escaparHTML(descripcion)}" form="form-${id}"></td>
                <td><div class="categoria-scroll"><select name="categoria" form="form-${id}">${opcionesCategoria}</select></div></td>
                <td><input type="number" name="precio" value="${precio}" step="10" form="form-${id}" required></td>
                <td>
                    <form method="POST" action="${formAction}" enctype="multipart/form-data" id="form-${id}">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrf}">
                        <button type="submit">Guardar</button>
                        <button type="button" onclick="cancelarEdicion('${id}', '${escaparHTML(nombre)}', '${escaparHTML(descripcion)}', '${precio}', '${escaparHTML(categoriaTexto)}', '${categoriaActual}')">Cancelar</button>
                    </form>
                </td>
            `;
        }

        const categoriasOpciones = window.categoriasOpciones;

        function cancelarEdicion(id, nombre, descripcion, precio, categoriaTexto, categoriaId) {
            // Usar la función auxiliar para construir la URL
            const eliminarUrl = construirUrlEliminacion(id);
            const fila = document.getElementById(`row-${id}`);

            // Recuperamos la imagen actual que estaba antes
            const imagenHTML = document.querySelector(`#row-${id} td:nth-child(2) div`)?.innerHTML || "Sin imagen";

            fila.innerHTML = `
                <td>${id}</td>
                <td id="imagen-${id}">${imagenHTML}</td>
                <td><span id="nombre-${id}">${nombre}</span></td>
                <td><span id="descripcion-${id}">${descripcion}</span></td>
                <td><span id="categoria-${id}" data-valor="${categoriaId}">${categoriaTexto}</span></td>
                <td><span id="precio-${id}">${precio}</span></td>
                <td id="acciones-${id}">
                    <button type="button" onclick="activarEdicion('${id}')">Editar</button>
                    <form method="POST" action="${eliminarUrl}" style="display:inline;">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${window.csrfToken}">
                        <button type="submit" style="background-color:red;" onclick="return confirm('¿Eliminar este producto?')">Eliminar</button>
                    </form>
                </td>
            `;
        }


        function mostrarModal() {
            const formProducto = document.getElementById('formAgregarProducto');
            if (formProducto) formProducto.reset();

            document.getElementById("modalProducto").style.display = "block";
        }

        function cerrarModal() {
            document.getElementById("modalProducto").style.display = "none";
        }

        window.onclick = function(event) {
            const modal = document.getElementById("modalProducto");
            if (event.target == modal) {
                modal.style.display = "none";
            }
        }

        function mostrarModalCategoria() {
            const formCategoria = document.getElementById('formAgregarCategoria');
            if (formCategoria) formCategoria.reset();

            document.getElementById("modalCategoria").style.display = "block";
        }

        function cerrarModalCategoria() {
            document.getElementById("modalCategoria").style.display = "none";
        }

        window.onclick = function(event) {
            if (event.target == document.getElementById("modalProducto")) {
                document.getElementById("modalProducto").style.display = "none";
            }
            if (event.target == document.getElementById("modalCategoria")) {
                document.getElementById("modalCategoria").style.display = "none";
            }
        }

        function marcarBorrarImagen(id) {
            const inputHidden = document.getElementById(`borrar-imagen-${id}`);
            const boton = document.getElementById(`btn-borrar-imagen-${id}`);

            if (inputHidden.value === "0") {
                inputHidden.value = "1";  // Marca para borrar
                boton.textContent = "Imagen eliminada (click para revertir)";
            } else {
                inputHidden.value = "0";  // Desmarca borrar
                boton.textContent = "Eliminar imagen";
            }
        }