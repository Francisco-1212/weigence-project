// Variables globales
let currentProduct = null;
let editMode = false;
let currentFilters = {
    category: '',
    status: '',
    dateStart: '',
    dateEnd: ''
};
let searchInput;
let productTable;
let productRows;

// Función para cerrar el modal
function cerrarModal() {
  const modal = document.getElementById('productModal');
  if (modal) {
    modal.classList.add('hidden');
  }
  editMode = false;
  currentProduct = null;
}

// Función para mostrar detalles del producto
function mostrarDetalles(producto) {
  const modal = document.getElementById('productModal');
  const modalTitle = document.getElementById('modalTitle');
  const modalContent = document.getElementById('modalContent');
  
  if (!modal || !modalTitle || !modalContent) return;
  
  currentProduct = producto;
  modalTitle.textContent = `Detalles del Producto: ${producto.nombre}`;
  
  modalContent.innerHTML = `
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
      <div class="bg-[#181E21] p-4 rounded-lg">
        <h4 class="text-lg font-semibold mb-3 text-[var(--primary-color)]">Información Básica</h4>
        <div class="space-y-2">
          <p><span class="font-medium">ID:</span> ${producto.idproducto}</p>
          <p><span class="font-medium">Nombre:</span> ${producto.nombre}</p>
          <p><span class="font-medium">Categoría:</span> ${producto.categoria}</p>
          <p><span class="font-medium">Stock:</span> ${producto.stock}</p>
          <p><span class="font-medium">Peso:</span> ${producto.peso} g</p>
          <p><span class="font-medium">Descripción:</span> ${producto.descripcion}</p>
          <p><span class="font-medium">Estante:</span> ${producto.d_estante || 'N/A'}</p>
        </div>
      </div>
      
      <div class="bg-[#181E21] p-4 rounded-lg">
        <h4 class="text-lg font-semibold mb-3 text-[var(--primary-color)]">Información de Auditoría</h4>
        <div class="space-y-2">
          <p><span class="font-medium">Fecha de Ingreso:</span> ${producto.fecha_ingreso || 'N/A'}</p>
          <p><span class="font-medium">Ingresado por:</span> ${producto.ingresado_por || 'N/A'}</p>
          <p><span class="font-medium">Modificado por:</span> ${producto.modificado_por || 'N/A'}</p>
          <p><span class="font-medium">Fecha de Modificación:</span> ${producto.fecha_modificacion || 'N/A'}</p>
        </div>
      </div>
    </div>
    
    <div class="flex justify-end space-x-3">
      <button class="px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded-md btn-cerrar">Cerrar</button>
      <button class="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-md btn-eliminar">Eliminar</button>
      <button class="px-4 py-2 bg-[var(--primary-color)] hover:bg-opacity-90 rounded-md btn-editar">Editar</button>
    </div>
  `;
  
  modal.classList.remove('hidden');
}

// Función para editar producto
function editarProducto() {
  if (!currentProduct) return;
  
  const modalTitle = document.getElementById('modalTitle');
  const modalContent = document.getElementById('modalContent');
  
  if (!modalTitle || !modalContent) return;
  
  editMode = true;
  modalTitle.textContent = `Editar Producto: ${currentProduct.nombre}`;
  
  modalContent.innerHTML = `
    <form id="editProductForm" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">ID Producto</label>
          <input type="text" value="${currentProduct.idproducto}" class="w-full bg-[#181E21] border border-gray-700 rounded-md px-3 py-2" disabled>
        </div>
        
        <div>
          <label class="block text-sm font-medium mb-1">Nombre *</label>
          <input type="text" name="nombre" value="${currentProduct.nombre}" class="w-full bg-[#181E21] border border-gray-700 rounded-md px-3 py-2" required>
        </div>
        
        <div>
          <label class="block text-sm font-medium mb-1">Categoría *</label>
          <input type="text" name="categoria" value="${currentProduct.categoria}" class="w-full bg-[#181E21] border border-gray-700 rounded-md px-3 py-2" required>
        </div>
        
        <div>
          <label class="block text-sm font-medium mb-1">Stock *</label>
          <input type="number" name="stock" value="${currentProduct.stock}" class="w-full bg-[#181E21] border border-gray-700 rounded-md px-3 py-2" required min="0">
        </div>
        
        <div>
          <label class="block text-sm font-medium mb-1">Peso (gramos) *</label>
          <input type="number" name="peso" value="${currentProduct.peso}" class="w-full bg-[#181E21] border border-gray-700 rounded-md px-3 py-2" required min="0">
        </div>
        
        <div>
          <label class="block text-sm font-medium mb-1">Estante</label>
          <input type="text" name="d_estante" value="${currentProduct.d_estante || ''}" class="w-full bg-[#181E21] border border-gray-700 rounded-md px-3 py-2">
        </div>
      </div>
      
      <div>
        <label class="block text-sm font-medium mb-1">Descripción</label>
        <textarea name="descripcion" class="w-full bg-[#181E21] border border-gray-700 rounded-md px-3 py-2" rows="3">${currentProduct.descripcion || ''}</textarea>
      </div>
      
      <div class="bg-[#181E21] p-4 rounded-lg mt-4">
        <h4 class="text-lg font-semibold mb-3 text-[var(--primary-color)]">Información de Auditoría (solo lectura)</h4>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Fecha de Ingreso</label>
            <input type="text" value="${currentProduct.fecha_ingreso || 'N/A'}" class="w-full bg-[#181E21] border border-gray-700 rounded-md px-3 py-2" disabled>
          </div>
          
          <div>
            <label class="block text-sm font-medium mb-1">Ingresado por</label>
            <input type="text" value="${currentProduct.ingresado_por || 'N/A'}" class="w-full bg-[#181E21] border border-gray-700 rounded-md px-3 py-2" disabled>
          </div>
          
          <div>
            <label class="block text-sm font-medium mb-1">Modificado por</label>
            <input type="text" value="${currentProduct.modificado_por || 'N/A'}" class="w-full bg-[#181E21] border border-gray-700 rounded-md px-3 py-2" disabled>
          </div>
          
          <div>
            <label class="block text-sm font-medium mb-1">Fecha de Modificación</label>
            <input type="text" value="${currentProduct.fecha_modificacion || 'N/A'}" class="w-full bg-[#181E21] border border-gray-700 rounded-md px-3 py-2" disabled>
          </div>
        </div>
      </div>
      
      <div class="flex justify-end space-x-3 pt-4">
        <button type="button" class="px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded-md btn-cancelar">Cancelar</button>
        <button type="submit" class="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-md">Guardar Cambios</button>
      </div>
    </form>
  `;
}

// Función para guardar los cambios del producto
function guardarCambiosProducto(form) {
  const formData = new FormData(form);
  const updatedProduct = {
    idproducto: currentProduct.idproducto,
    nombre: formData.get('nombre'),
    categoria: formData.get('categoria'),
    stock: parseInt(formData.get('stock')),
    peso: parseInt(formData.get('peso')),
    descripcion: formData.get('descripcion'),
    d_estante: formData.get('d_estante'),
    fecha_ingreso: currentProduct.fecha_ingreso,
    ingresado_por: currentProduct.ingresado_por,
    modificado_por: 'Usuario Actual',
    fecha_modificacion: new Date().toLocaleString()
  };
  
  // Simular envío al servidor
  console.log('Datos a enviar al servidor:', updatedProduct);
  
  // Simular respuesta exitosa
  setTimeout(() => {
    currentProduct = {...currentProduct, ...updatedProduct};
    alert('¡Producto actualizado correctamente!');
    mostrarDetalles(currentProduct);
  }, 500);
}

// Función para eliminar producto
function eliminarProducto(id) {
  if (confirm(`¿Estás seguro de que deseas eliminar el producto con ID: ${id}?`)) {
    console.log('Eliminando producto con ID:', id);
    alert(`Producto con ID: ${id} eliminado (simulación).`);
    cerrarModal();
  }
}

// Funciones nuevas de filtrado
function setupDropdowns() {
    // Dropdown Categoría
    const categoryBtn = document.getElementById('categoryBtn');
    const categoryDropdown = document.getElementById('categoryDropdown');
    const categoryOptions = document.querySelectorAll('.category-option');

    if (categoryBtn) {
        categoryBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            categoryDropdown.classList.toggle('hidden');
            document.getElementById('statusDropdown')?.classList.add('hidden');
            document.getElementById('dateRangeDropdown')?.classList.add('hidden');
        });
    }
    categoryOptions?.forEach(option => {
        option.addEventListener('click', function() {
            const category = this.getAttribute('data-category');
            currentFilters.category = category;
            categoryBtn.querySelector('p').textContent = category || 'Categoría';
            categoryDropdown.classList.add('hidden');
            filterProducts();
        });
    });

    // Configurar dropdown de Estado
    const statusBtn = document.getElementById('statusBtn');
    const statusDropdown = document.getElementById('statusDropdown');
    const statusOptions = document.querySelectorAll('.status-option');

    if (statusBtn) {
        statusBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            statusDropdown.classList.toggle('hidden');
            categoryDropdown?.classList.add('hidden');
            document.getElementById('dateRangeDropdown')?.classList.add('hidden');
        });
    }

    if (statusOptions) {
        statusOptions.forEach(option => {
            option.addEventListener('click', function() {
                const status = this.getAttribute('data-status');
                currentFilters.status = status;
                statusBtn.querySelector('p').textContent = this.textContent;
                statusDropdown.classList.add('hidden');
                filterProducts();
            });
        });
    }

    // Configurar dropdown de Fechas
    setupDateRangeDropdown();
}

function filterProducts() {
    if (!productRows) return;
    
    const searchTerm = searchInput?.value.toLowerCase() || '';
    let visibleCount = 0;

    productRows.forEach(row => {
        const name = row.getAttribute('data-name') || '';
        const category = row.getAttribute('data-category') || '';
        const stock = parseInt(row.getAttribute('data-stock')) || 0;
        const dateStr = row.getAttribute('data-date');
        
        let visible = true;

        // Aplicar filtros
        if (searchTerm && !name.includes(searchTerm)) {
            visible = false;
        }

        if (currentFilters.category && category !== currentFilters.category) {
            visible = false;
        }

        if (currentFilters.status) {
            if (currentFilters.status === 'normal' && stock < 10) visible = false;
            if (currentFilters.status === 'bajo' && (stock >= 10 || stock === 0)) visible = false;
            if (currentFilters.status === 'agotado' && stock !== 0) visible = false;
        }

        if (currentFilters.dateStart && currentFilters.dateEnd && dateStr) {
            const date = new Date(dateStr);
            const startDate = new Date(currentFilters.dateStart);
            const endDate = new Date(currentFilters.dateEnd);
            endDate.setHours(23, 59, 59);

            if (isNaN(date.getTime())) {
                visible = false;
            } else if (date < startDate || date > endDate) {
                visible = false;
            }
        }

        row.style.display = visible ? '' : 'none';
        if (visible) visibleCount++;
    });

    updateFilterUI(visibleCount);
}

// Función para manejar el rango de fechas
function setupDateRangeDropdown() {
    const dateRangeBtn = document.getElementById('dateRangeBtn');
    const dateRangeDropdown = document.getElementById('dateRangeDropdown');
    const applyDateRange = document.getElementById('applyDateRange');
    const clearDateRange = document.getElementById('clearDateRange');

    if (dateRangeBtn) {
        dateRangeBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            dateRangeDropdown.classList.toggle('hidden');
            document.getElementById('categoryDropdown')?.classList.add('hidden');
            document.getElementById('statusDropdown')?.classList.add('hidden');
        });
    }

    if (applyDateRange) {
        applyDateRange.addEventListener('click', function() {
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;
            
            if (!startDate || !endDate) {
                alert('Por favor seleccione ambas fechas');
                return;
            }

            currentFilters.dateStart = startDate;
            currentFilters.dateEnd = endDate;
            dateRangeDropdown.classList.add('hidden');
            filterProducts();
        });
    }

    if (clearDateRange) {
        clearDateRange.addEventListener('click', function() {
            document.getElementById('startDate').value = '';
            document.getElementById('endDate').value = '';
            currentFilters.dateStart = '';
            currentFilters.dateEnd = '';
            dateRangeBtn.querySelector('p').textContent = 'Rango de Fechas';
            dateRangeDropdown.classList.add('hidden');
            filterProducts();
        });
    }
}

// Función para manejar la exportación
function exportProducts() {
    const visibleRows = Array.from(productRows).filter(row => row.style.display !== 'none');
    
    if (visibleRows.length === 0) {
        alert('No hay datos para exportar');
        return;
    }

    const csv = generateCSV(visibleRows);
    downloadCSV(csv);
}

function generateCSV(rows) {
    let csv = 'ID/Código,Nombre,Categoría,Stock Actual,Peso Unitario,Peso Total,Estado,Última Actualización\n';
    
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        const rowData = [];
        for (let i = 0; i < cells.length - 1; i++) {
            let cellText = cells[i].textContent.trim();
            if (cellText.includes(',') || cellText.includes('"')) {
                cellText = '"' + cellText.replace(/"/g, '""') + '"';
            }
            rowData.push(cellText);
        }
        csv += rowData.join(',') + '\n';
    });

    return csv;
}

function downloadCSV(csv) {
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'inventario_' + new Date().toISOString().split('T')[0] + '.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function updateFilterUI(visibleCount) {
    const dateRangeBtn = document.getElementById('dateRangeBtn');
    if (dateRangeBtn && currentFilters.dateStart && currentFilters.dateEnd) {
        const start = new Date(currentFilters.dateStart).toLocaleDateString();
        const end = new Date(currentFilters.dateEnd).toLocaleDateString();
        dateRangeBtn.querySelector('p').textContent = `${start} - ${end}`;
    }

    const noProductsRow = document.getElementById('noProductsRow');
    if (noProductsRow) {
        noProductsRow.style.display = visibleCount === 0 ? '' : 'none';
        if (visibleCount === 0) {
            noProductsRow.querySelector('td').textContent = 'No se encontraron productos que coincidan con los filtros';
        }
    }
}

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar variables de filtrado
    searchInput = document.getElementById('searchInput');
    productTable = document.getElementById('productTable');
    productRows = document.querySelectorAll('.product-row');
    
    // Configurar búsqueda
    if (searchInput) {
        searchInput.addEventListener('input', filterProducts);
    }

    // Configurar dropdowns y filtros
    setupDropdowns();

    // Configurar exportación
    const exportBtn = document.getElementById('exportBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportProducts);
    }

    // --- Configuración del Modal ---
    const modal = document.getElementById('productModal');
    const closeModal = document.getElementById('closeModal');
    const gestionarBtns = document.querySelectorAll('.gestionar-btn');
    const modalContent = document.getElementById('modalContent');
    
    // Evento para cerrar el modal con la X
    if (closeModal) {
        closeModal.addEventListener('click', cerrarModal);
    }
    
    // Cerrar modal al hacer clic fuera del contenido
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                cerrarModal();
            }
        });
    }
    
    // Event delegation para los botones dentro del modal
    if (modalContent) {
        modalContent.addEventListener('click', function(e) {
            // Botón Cerrar
            if (e.target.classList.contains('btn-cerrar')) {
                cerrarModal();
            }
            // Botón Eliminar
            else if (e.target.classList.contains('btn-eliminar')) {
                if (currentProduct) {
                    eliminarProducto(currentProduct.idproducto);
                }
            }
            // Botón Editar
            else if (e.target.classList.contains('btn-editar')) {
                editarProducto();
            }
            // Botón Cancelar (en modo edición)
            else if (e.target.classList.contains('btn-cancelar')) {
                if (currentProduct) {
                    mostrarDetalles(currentProduct);
                }
            }
        });
        
        // Event listener para el formulario de edición
        modalContent.addEventListener('submit', function(e) {
            if (e.target.id === 'editProductForm') {
                e.preventDefault();
                guardarCambiosProducto(e.target);
            }
        });
    }
    
    // Añadir eventos a los botones de gestionar
    if (gestionarBtns) {
        gestionarBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                try {
                    const producto = JSON.parse(this.getAttribute('data-producto'));
                    mostrarDetalles(producto);
                } catch (e) {
                    console.error('Error al parsear datos del producto:', e);
                }
            });
        });
    }

    // Cerrar dropdowns al hacer clic fuera
    document.addEventListener('click', function() {
        document.getElementById('categoryDropdown')?.classList.add('hidden');
        document.getElementById('statusDropdown')?.classList.add('hidden');
        document.getElementById('dateRangeDropdown')?.classList.add('hidden');
    });
});

