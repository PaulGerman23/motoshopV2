/* ============================================
   BÚSQUEDA EN TIEMPO REAL
============================================ */
document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById('searchInput');
    const tablaUsuarios = document.getElementById('tablaUsuarios');

    if (searchInput && tablaUsuarios) {
        searchInput.addEventListener('keyup', function () {
            const filter = this.value.toUpperCase();
            const rows = tablaUsuarios.querySelectorAll("tbody tr");

            rows.forEach(row => {
                const cells = row.querySelectorAll("td");
                let visible = false;

                cells.forEach(td => {
                    if (td.innerText.toUpperCase().includes(filter)) {
                        visible = true;
                    }
                });

                row.style.display = visible ? "" : "none";
            });
        });
    }
});

/* ============================================
   VER DETALLE DEL USUARIO (MODAL)
============================================ */
function verDetalleUsuario(btn) {
    const id = btn.dataset.id;
    const modalBody = document.getElementById('modalUsuarioBody');

    modalBody.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
        </div>
    `;

    setTimeout(() => {
        const row = document.querySelector(`tr[data-usuario-id="${id}"]`);
        if (!row) return;

        const userName = row.querySelector('.user-name')?.textContent || "Sin nombre";
        const avatarText = row.querySelector('.user-avatar')?.textContent || "?";

        modalBody.innerHTML = `
            <div class="row g-4">

                <div class="col-md-4 text-center">
                    <div class="product-detail-image">
                        <div style="font-size: 48px; font-weight: 700;">${avatarText}</div>
                    </div>
                    <div class="mt-3">
                        <span class="status-badge status-active">Activo</span>
                    </div>
                </div>

                <div class="col-md-8">
                    <h4>${userName}</h4>
                    <p class="text-muted">Información completa del usuario</p>
                </div>

            </div>
        `;
    }, 300);
}


/* ============================================
   CONFIRMAR ELIMINACIÓN
============================================ */
function confirmarEliminar(btn) {
    const id = btn.dataset.id;
    const nombre = btn.dataset.nombre;

    document.getElementById('usuarioEliminarNombre').textContent = nombre;
    document.getElementById('formEliminar').action = `/usuarios/eliminar/${id}/`;

    const modal = new bootstrap.Modal(document.getElementById('modalEliminar'));
    modal.show();
}


/* ============================================
   EXPORTAR AL ÁMBITO GLOBAL
============================================ */
window.verDetalleUsuario = verDetalleUsuario;
window.confirmarEliminar = confirmarEliminar;
