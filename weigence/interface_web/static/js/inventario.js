let currentProduct = null;
let editMode = false;

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

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
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
});
