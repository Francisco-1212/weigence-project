/**
 * Gestión de Usuarios - Script principal
 * Maneja crear, editar, eliminar y listar usuarios
 */

let usuarios_global = [];
let modo_modal = 'crear'; // 'crear' o 'editar'

// ============================================================
// INICIALIZACIÓN
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
  console.log('[USUARIOS] Script inicializado');
  
  // Cargar lista de usuarios
  cargarUsuarios();
  
  // Event listeners
  document.getElementById('btn-crear-usuario').addEventListener('click', abrirModalCrear);
  document.getElementById('cerrar-modal').addEventListener('click', cerrarModal);
  document.getElementById('usuario-form').addEventListener('submit', guardarUsuario);
  
  // Cerrar modal al hacer click en overlay
  document.getElementById('usuario-modal').addEventListener('click', function(e) {
    if (e.target === this) cerrarModal();
  });
});

// ============================================================
// CARGAR USUARIOS
// ============================================================
function cargarUsuarios() {
  console.log('[USUARIOS] Cargando lista de usuarios...');
  
  fetch('/api/usuarios', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  })
  .then(data => {
    if (data.success) {
      usuarios_global = data.data;
      mostrarUsuarios(data.data);
      console.log(`[USUARIOS] ${data.data.length} usuarios cargados`);
    } else {
      mostrarError('Error al cargar usuarios: ' + data.error);
    }
  })
  .catch(error => {
    console.error('[USUARIOS] Error:', error);
    mostrarError('Error al cargar usuarios');
  });
}

// ============================================================
// MOSTRAR USUARIOS EN TABLA
// ============================================================
function mostrarUsuarios(usuarios) {
  const tbody = document.getElementById('usuarios-tabla');
  
  if (!usuarios || usuarios.length === 0) {
    tbody.innerHTML = `
      <tr class="text-center py-8">
        <td colspan="7" class="py-8 text-gray-500 dark:text-gray-400">
          No hay usuarios registrados
        </td>
      </tr>
    `;
    return;
  }
  
  tbody.innerHTML = usuarios.map(usuario => `
    <tr class="border-t dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition">
      <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">${usuario.rut_usuario}</td>
      <td class="px-6 py-4 text-sm text-gray-900 dark:text-white font-medium">${usuario.nombre}</td>
      <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">${usuario.correo}</td>
      <td class="px-6 py-4 text-sm">
        <span class="px-3 py-1 rounded-full text-xs font-medium ${obtenerColorRol(usuario.rol)}">
          ${formatearRol(usuario.rol)}
        </span>
      </td>
      <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">${usuario['numero celular'] || '-'}</td>
      <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">${formatearFecha(usuario.fecha_registro)}</td>
      <td class="px-6 py-4 text-right space-x-2">
        <button 
          onclick="abrirModalEditar('${usuario.rut_usuario}')"
          class="px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white text-xs rounded transition"
        >
          <span class="material-symbols-outlined text-sm">edit</span>
        </button>
        <button 
          onclick="eliminarUsuario('${usuario.rut_usuario}', '${usuario.nombre}')"
          class="px-3 py-1 bg-red-500 hover:bg-red-600 text-white text-xs rounded transition"
        >
          <span class="material-symbols-outlined text-sm">delete</span>
        </button>
      </td>
    </tr>
  `).join('');
}

// ============================================================
// MODAL CREAR
// ============================================================
function abrirModalCrear() {
  console.log('[USUARIOS] Abriendo modal para crear usuario');
  
  modo_modal = 'crear';
  limpiarFormulario();
  
  document.getElementById('modal-titulo').textContent = 'Nuevo Usuario';
  document.getElementById('usuario-rut').disabled = false;
  document.getElementById('usuario-modal').classList.remove('hidden');
}

// ============================================================
// MODAL EDITAR
// ============================================================
function abrirModalEditar(rut) {
  console.log(`[USUARIOS] Abriendo modal para editar usuario: ${rut}`);
  
  modo_modal = 'editar';
  limpiarFormulario();
  
  const usuario = usuarios_global.find(u => u.rut_usuario === rut);
  if (!usuario) {
    mostrarError('Usuario no encontrado');
    return;
  }
  
  document.getElementById('modal-titulo').textContent = `Editar Usuario: ${usuario.nombre}`;
  document.getElementById('usuario-rut-original').value = rut;
  document.getElementById('usuario-rut').value = rut;
  document.getElementById('usuario-rut').disabled = true; // RUT no se puede cambiar
  document.getElementById('usuario-nombre').value = usuario.nombre;
  document.getElementById('usuario-correo').value = usuario.correo;
  document.getElementById('usuario-rol').value = usuario.rol;
  document.getElementById('usuario-telefono').value = usuario['numero celular'] || '';
  
  document.getElementById('usuario-modal').classList.remove('hidden');
}

// ============================================================
// CERRAR MODAL
// ============================================================
function cerrarModal() {
  document.getElementById('usuario-modal').classList.add('hidden');
  limpiarFormulario();
}

// ============================================================
// LIMPIAR FORMULARIO
// ============================================================
function limpiarFormulario() {
  document.getElementById('usuario-form').reset();
  document.getElementById('usuario-rut-original').value = '';
  document.querySelectorAll('[id^="error-"]').forEach(el => el.classList.add('hidden'));
}

// ============================================================
// GUARDAR USUARIO
// ============================================================
function guardarUsuario(e) {
  e.preventDefault();
  
  // Limpiar errores previos
  document.querySelectorAll('[id^="error-"]').forEach(el => el.classList.add('hidden'));
  
  // Obtener datos del formulario
  const rut = document.getElementById('usuario-rut').value.trim();
  const nombre = document.getElementById('usuario-nombre').value.trim();
  const correo = document.getElementById('usuario-correo').value.trim();
  const rol = document.getElementById('usuario-rol').value.trim();
  const telefono = document.getElementById('usuario-telefono').value.trim();
  
  // Validaciones
  let errores = {};
  
  if (!rut) {
    errores.rut = 'El RUT es requerido';
  } else if (!validarRUT(rut)) {
    errores.rut = 'Formato de RUT inválido (ej: 20123456-7)';
  }
  
  if (!nombre) {
    errores.nombre = 'El nombre es requerido';
  } else if (nombre.length < 3) {
    errores.nombre = 'El nombre debe tener al menos 3 caracteres';
  }
  
  if (!correo) {
    errores.correo = 'El correo es requerido';
  } else if (!validarEmail(correo)) {
    errores.correo = 'Formato de correo inválido';
  }
  
  if (!rol) {
    errores.rol = 'El rol es requerido';
  }
  
  // Mostrar errores
  if (Object.keys(errores).length > 0) {
    for (let campo in errores) {
      const elError = document.getElementById(`error-${campo}`);
      if (elError) {
        elError.textContent = errores[campo];
        elError.classList.remove('hidden');
      }
    }
    return;
  }
  
  // Preparar datos
  const datosUsuario = {
    rut_usuario: rut,
    nombre: nombre,
    correo: correo,
    rol: rol,
    'numero celular': telefono,
    fecha_registro: new Date().toISOString()
  };
  
  // Enviar al servidor
  if (modo_modal === 'crear') {
    crearUsuario(datosUsuario);
  } else {
    editarUsuario(rut, datosUsuario);
  }
}

// ============================================================
// CREAR USUARIO (API)
// ============================================================
function crearUsuario(datos) {
  console.log('[USUARIOS] Creando nuevo usuario...', datos);
  
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
  
  fetch('/api/usuarios', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken
    },
    body: JSON.stringify(datos)
  })
  .then(response => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  })
  .then(data => {
    if (data.success) {
      mostrarExito('Usuario creado exitosamente');
      cerrarModal();
      cargarUsuarios();
      console.log('[USUARIOS] Usuario creado');
    } else {
      mostrarError('Error al crear usuario: ' + (data.error || 'Error desconocido'));
    }
  })
  .catch(error => {
    console.error('[USUARIOS] Error:', error);
    mostrarError('Error al crear usuario');
  });
}

// ============================================================
// EDITAR USUARIO (API)
// ============================================================
function editarUsuario(rut, datos) {
  console.log('[USUARIOS] Editando usuario:', rut, datos);
  
  fetch(`/api/usuarios/${rut}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(datos)
  })
  .then(response => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  })
  .then(data => {
    if (data.success) {
      mostrarExito('Usuario actualizado exitosamente');
      cerrarModal();
      cargarUsuarios();
      console.log('[USUARIOS] Usuario actualizado');
    } else {
      mostrarError('Error al actualizar usuario: ' + (data.error || 'Error desconocido'));
    }
  })
  .catch(error => {
    console.error('[USUARIOS] Error:', error);
    mostrarError('Error al actualizar usuario');
  });
}

// ============================================================
// ELIMINAR USUARIO
// ============================================================
function eliminarUsuario(rut, nombre) {
  if (!confirm(`¿Estás seguro de que deseas eliminar a ${nombre}?`)) {
    return;
  }
  
  console.log('[USUARIOS] Eliminando usuario:', rut);
  
  fetch(`/api/usuarios/${rut}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  })
  .then(data => {
    if (data.success) {
      mostrarExito('Usuario eliminado exitosamente');
      cargarUsuarios();
      console.log('[USUARIOS] Usuario eliminado');
    } else {
      mostrarError('Error al eliminar usuario: ' + (data.error || 'Error desconocido'));
    }
  })
  .catch(error => {
    console.error('[USUARIOS] Error:', error);
    mostrarError('Error al eliminar usuario');
  });
}

// ============================================================
// UTILIDADES
// ============================================================

function validarRUT(rut) {
  // Formato: XX.XXX.XXX-X o XXXXXXXX-X
  return /^(\d{1,2}\.\d{3}\.\d{3}-\d|\d{7,8}-\d)$/.test(rut);
}

function validarEmail(email) {
  return /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email);
}

function formatearRol(rol) {
  const roles = {
    'farmaceutico': 'Farmacéutico',
    'bodeguera': 'Bodeguera',
    'supervisor': 'Supervisor',
    'jefe': 'Jefe',
    'administrador': 'Administrador'
  };
  return roles[rol] || rol;
}

function obtenerColorRol(rol) {
  const colores = {
    'farmaceutico': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'bodeguera': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    'supervisor': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    'jefe': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    'administrador': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
  };
  return colores[rol] || 'bg-gray-100 text-gray-800';
}

function formatearFecha(fecha) {
  if (!fecha) return '-';
  try {
    const date = new Date(fecha);
    return date.toLocaleDateString('es-CL', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });
  } catch {
    return fecha;
  }
}

function mostrarExito(mensaje) {
  console.log('[USUARIOS] Éxito:', mensaje);
  // Mostrar notificación (puedes usar un toast o alert)
  alert(mensaje);
}

function mostrarError(mensaje) {
  console.error('[USUARIOS] Error:', mensaje);
  // Mostrar notificación (puedes usar un toast o alert)
  alert('❌ ' + mensaje);
}
