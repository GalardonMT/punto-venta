const csrfToken = window.csrfToken || '';

function construirUrlEdicion(id) {
    if (window.editarProductoUrl && window.editarProductoUrl.includes('0')) {
        return window.editarProductoUrl.replace('0', id);
    }
    return `/productos/editar/${id}/`;
}

document.addEventListener('DOMContentLoaded', () => {
    if (!csrfToken || !window.editarProductoUrl) {
        console.error('Variables globales no definidas correctamente');
    }

    const modalProducto = document.getElementById('modalProducto');
    const modalCategoria = document.getElementById('modalCategoria');
    const modalEditarProducto = document.getElementById('modalEditarProducto');
    const formEditarProducto = document.getElementById('formEditarProducto');
    const editarProductoId = document.getElementById('editarProductoId');
    const editarNombre = document.getElementById('editarNombre');
    const editarDescripcion = document.getElementById('editarDescripcion');
    const editarPrecio = document.getElementById('editarPrecio');
    const editarCategoria = document.getElementById('editarCategoria');
    const editarImagen = document.getElementById('editarImagen');
    const editarImagenPreview = document.getElementById('editarImagenPreview');
    const editarBorrarImagen = document.getElementById('editarBorrarImagen');
    const toggleImagenBtn = document.getElementById('btnToggleImagen');

    const setPreviewContent = (url) => {
        if (url) {
            editarImagenPreview.innerHTML = `<img src="${url}" alt="Imagen actual">`;
            editarImagenPreview.dataset.url = url;
        } else {
            editarImagenPreview.innerHTML = '<span>Sin imagen registrada</span>';
            editarImagenPreview.dataset.url = '';
        }
        editarImagenPreview.classList.remove('imagen-eliminada');
    };

    const resetEditarForm = () => {
        formEditarProducto.reset();
        editarCategoria.value = '';
        editarProductoId.value = '';
        editarBorrarImagen.value = '0';
        setPreviewContent('');
        toggleImagenBtn.disabled = true;
        toggleImagenBtn.textContent = 'No hay imagen para eliminar';
    };

    window.abrirModalEditarProducto = (button) => {
        const id = button.dataset.id;
        if (!id) return;

        const nombre = document.getElementById(`nombre-${id}`)?.textContent.trim() || '';
        const descripcion = document.getElementById(`descripcion-${id}`)?.textContent.trim() || '';
        const precio = document.getElementById(`precio-${id}`)?.textContent.trim() || '';
        const categoriaSpan = document.getElementById(`categoria-${id}`);
        const categoriaId = categoriaSpan?.dataset.valor || '';

        editarProductoId.value = id;
        editarNombre.value = nombre;
        editarDescripcion.value = descripcion;
        editarPrecio.value = precio.replace(',', '.');
        editarCategoria.value = categoriaId;
        editarImagen.value = '';
        editarBorrarImagen.value = '0';

        const imagenUrl = button.dataset.imagenUrl || '';
        setPreviewContent(imagenUrl);

        if (imagenUrl) {
            toggleImagenBtn.disabled = false;
            toggleImagenBtn.textContent = 'Eliminar imagen actual';
        } else {
            toggleImagenBtn.disabled = true;
            toggleImagenBtn.textContent = 'No hay imagen para eliminar';
        }

        formEditarProducto.setAttribute('action', construirUrlEdicion(id));
        modalEditarProducto.style.display = 'block';
    };

    window.cerrarModalEditarProducto = () => {
        resetEditarForm();
        modalEditarProducto.style.display = 'none';
    };

    window.toggleEliminarImagenEditar = () => {
        if (toggleImagenBtn.disabled) return;
        if (editarBorrarImagen.value === '0') {
            editarBorrarImagen.value = '1';
            toggleImagenBtn.textContent = 'Restaurar imagen';
            editarImagenPreview.classList.add('imagen-eliminada');
        } else {
            editarBorrarImagen.value = '0';
            toggleImagenBtn.textContent = 'Eliminar imagen actual';
            editarImagenPreview.classList.remove('imagen-eliminada');
        }
    };

    window.enviarEdicionProducto = async (event) => {
        event.preventDefault();
        const id = editarProductoId.value;
        if (!id) return;

        const url = formEditarProducto.getAttribute('action') || construirUrlEdicion(id);
        const formData = new FormData(formEditarProducto);

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'X-CSRFToken': csrfToken },
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Error al actualizar el producto');
            }

            window.location.reload();
        } catch (error) {
            console.error(error);
            showAppModal('No se pudo actualizar el producto. Intenta nuevamente.', {
                variant: 'danger',
                title: 'Error al actualizar producto'
            });
        }
    };

    if (editarImagen) {
        editarImagen.addEventListener('change', () => {
            if (editarImagen.files && editarImagen.files.length > 0) {
                editarImagenPreview.textContent = editarImagen.files[0].name;
                editarImagenPreview.classList.remove('imagen-eliminada');
                editarBorrarImagen.value = '0';
                toggleImagenBtn.disabled = false;
                toggleImagenBtn.textContent = 'Eliminar imagen actual';
            } else {
                setPreviewContent(editarImagenPreview.dataset.url || '');
            }
        });
    }

    window.mostrarModal = () => {
        const formProducto = document.getElementById('formAgregarProducto');
        if (formProducto) formProducto.reset();
        modalProducto.style.display = 'block';
    };

    window.cerrarModal = () => {
        modalProducto.style.display = 'none';
    };

    window.mostrarModalCategoria = () => {
        const formCategoria = document.getElementById('formAgregarCategoria');
        if (formCategoria) formCategoria.reset();
        modalCategoria.style.display = 'block';
    };

    window.cerrarModalCategoria = () => {
        modalCategoria.style.display = 'none';
    };

    window.addEventListener('click', (event) => {
        if (event.target === modalProducto) {
            window.cerrarModal();
        }
        if (event.target === modalCategoria) {
            window.cerrarModalCategoria();
        }
        if (event.target === modalEditarProducto) {
            window.cerrarModalEditarProducto();
        }
    });
});
