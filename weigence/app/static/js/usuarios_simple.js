/**
 * Gestión de Usuarios - Script Simple y Funcional
 */

console.log('[USUARIOS.JS] Script cargado');

// Esperar a que el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
  console.log('[USUARIOS] DOM listo, inicializando...');
  
  // Buscar elementos
  const btnCrear = document.getElementById('btn-crear-usuario');
  const btnCerrar = document.getElementById('cerrar-modal');
  const btnCancelar = document.getElementById('btn-cancelar');
  const btnGuardar = document.getElementById('btn-guardar');
  const tablaBody = document.getElementById('usuarios-tabla');
  const modal = document.getElementById('usuario-modal');
  const form = document.getElementById('usuario-form');
  
  console.log('[USUARIOS] Elementos encontrados:', {
    btnCrear: !!btnCrear,
    btnCerrar: !!btnCerrar,
    btnCancelar: !!btnCancelar,
    btnGuardar: !!btnGuardar,
    tablaBody: !!tablaBody,
    modal: !!modal,
    form: !!form
  });
  
  // Función: Cargar usuarios
  function cargarUsuarios() {
    console.log('[USUARIOS] Cargando usuarios...');
    
    fetch('/api/usuarios')
      .then(response => response.json())
      .then(data => {
        console.log('[USUARIOS] Datos recibidos:', data);
        
        if (!data.success) {
          tablaBody.innerHTML = `
            <tr>
              <td colspan="7" class="px-6 py-4 text-center text-red-500">
                Error: ${data.error}
              </td>
            </tr>
          `;
          return;
        }
        
        if (!data.data || data.data.length === 0) {
          tablaBody.innerHTML = `
            <tr>
              <td colspan="7" class="px-6 py-4 text-center text-gray-500 dark:text-gray-400">
                No hay usuarios registrados
              </td>
            </tr>
          `;
          return;
        }
        
        // Mostrar usuarios
        tablaBody.innerHTML = data.data.map(usuario => {
          const rolMinuscula = usuario.rol?.toLowerCase() || 'usuario';
          return `
          <tr class="border-t dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700">
            <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">${usuario.rut_usuario}</td>
            <td class="px-6 py-4 text-sm text-gray-900 dark:text-white font-medium">${usuario.nombre}</td>
            <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">${usuario.correo}</td>
            <td class="px-6 py-4 text-sm">
              <span class="px-3 py-1 rounded-full text-xs font-medium ${obtenerColorRol(rolMinuscula)}">
                ${formatearRol(rolMinuscula)}
              </span>
            </td>
            <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">${usuario['numero celular'] || '-'}</td>
            <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">${formatearFecha(usuario.fecha_registro)}</td>
            <td class="px-6 py-4 text-right space-x-2">
              <button onclick="editarUsuario('${usuario.rut_usuario}')" class="px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white text-xs rounded transition">
                ✏️ Editar
              </button>
              <button onclick="eliminarUsuario('${usuario.rut_usuario}', '${usuario.nombre}')" class="px-3 py-1 bg-red-500 hover:bg-red-600 text-white text-xs rounded transition">
                🗑️ Eliminar
              </button>
            </td>
          </tr>
          `;
        }).join('');
        
        console.log('[USUARIOS] Tabla actualizada con ' + data.data.length + ' usuarios');
      })
      .catch(error => {
        console.error('[USUARIOS] Error:', error);
        tablaBody.innerHTML = `
          <tr>
            <td colspan="7" class="px-6 py-4 text-center text-red-500">
              Error al cargar usuarios: ${error.message}
            </td>
          </tr>
        `;
      });
  }
  
  // Función: Abrir modal para crear
  function abrirModalCrear() {
    console.log('[USUARIOS] Abriendo modal para crear usuario');
    document.getElementById('modal-titulo').textContent = 'Nuevo Usuario';
    document.getElementById('usuario-rut').disabled = false;
    document.getElementById('usuario-rut-original').value = '';
    document.getElementById('requerida-contrasena').style.display = 'inline';
    form.reset();
    limpiarErrores();
    modal.classList.remove('hidden');
  }
  
  // Función: Cerrar modal
  function cerrarModal() {
    console.log('[USUARIOS] Cerrando modal');
    modal.classList.add('hidden');
    form.reset();
    limpiarErrores();
  }
  
  // Función: Limpiar errores
  function limpiarErrores() {
    document.querySelectorAll('[id^="error-"]').forEach(el => {
      el.classList.add('hidden');
      el.textContent = '';
    });
  }
  
  // Función: Editar usuario
  window.editarUsuario = function(rut) {
    console.log('[USUARIOS] Cargando usuario para editar:', rut);
    
    fetch(`/api/usuarios/${rut}`)
      .then(response => response.json())
      .then(data => {
        if (!data.success) {
          alert('Error: ' + data.error);
          return;
        }
        
        const usuario = data.data;
        console.log('[USUARIOS] Usuario cargado:', usuario);
        
        // Llenar formulario
        document.getElementById('modal-titulo').textContent = `Editar Usuario: ${usuario.nombre}`;
        document.getElementById('usuario-rut').disabled = true;
        document.getElementById('usuario-rut').value = usuario.rut_usuario;
        document.getElementById('usuario-rut-original').value = usuario.rut_usuario;
        document.getElementById('usuario-nombre').value = usuario.nombre;
        document.getElementById('usuario-correo').value = usuario.correo;
        document.getElementById('usuario-rol').value = usuario.rol;
        document.getElementById('usuario-telefono').value = usuario['numero celular'] || '';
        document.getElementById('usuario-contraseña').value = '';
        document.getElementById('requerida-contrasena').style.display = 'none';
        
        limpiarErrores();
        modal.classList.remove('hidden');
      })
      .catch(error => {
        console.error('[USUARIOS] Error:', error);
        alert('Error al cargar usuario: ' + error.message);
      });
  };
  
  // Función: Eliminar usuario
  window.eliminarUsuario = function(rut, nombre) {
    if (!confirm(`¿Estás seguro de que deseas eliminar a ${nombre}?`)) {
      return;
    }
    
    console.log('[USUARIOS] Eliminando usuario:', rut);
    
    fetch(`/api/usuarios/${rut}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' }
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          console.log('[USUARIOS] Usuario eliminado');
          alert('✅ Usuario eliminado correctamente');
          cargarUsuarios();
        } else {
          alert('❌ Error: ' + data.error);
        }
      })
      .catch(error => {
        console.error('[USUARIOS] Error:', error);
        alert('❌ Error al eliminar usuario');
      });
  };
  
  // Función: Guardar usuario (crear o editar)
  function guardarUsuario(e) {
    e.preventDefault();
    
    limpiarErrores();
    
    const rut = document.getElementById('usuario-rut').value.trim();
    const nombre = document.getElementById('usuario-nombre').value.trim();
    const correo = document.getElementById('usuario-correo').value.trim();
    const rol = document.getElementById('usuario-rol').value.trim();
    const telefono = document.getElementById('usuario-telefono').value.trim();
    const contraseña = document.getElementById('usuario-contraseña').value.trim();
    const rutOriginal = document.getElementById('usuario-rut-original').value;
    
    console.log('[USUARIOS] Validando formulario...', {rut, nombre, correo, rol, rutOriginal});
    
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
    
    if (!rutOriginal && !contraseña) {
      errores.contraseña = 'La contraseña es requerida para nuevos usuarios';
    }
    
    // Mostrar errores
    if (Object.keys(errores).length > 0) {
      console.log('[USUARIOS] Errores de validación:', errores);
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
    const datos = {
      rut_usuario: !rutOriginal ? rut : undefined,
      nombre,
      correo,
      rol,
      numero_celular: telefono || null,
      contraseña
    };
    
    // Eliminar undefined
    Object.keys(datos).forEach(key => datos[key] === undefined && delete datos[key]);
    
    console.log('[USUARIOS] Datos a enviar:', datos);
    
    // Enviar
    const metodo = rutOriginal ? 'PUT' : 'POST';
    const url = rutOriginal ? `/api/usuarios/${rutOriginal}` : '/api/usuarios';
    
    if (!rutOriginal) {
      datos.rut_usuario = rut;
    }
    
    console.log('[USUARIOS] Enviando:', {metodo, url, datos});
    
    btnGuardar.disabled = true;
    btnGuardar.textContent = '⏳ Guardando...';
    
    fetch(url, {
      method: metodo,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos)
    })
      .then(response => response.json())
      .then(data => {
        console.log('[USUARIOS] Respuesta:', data);
        
        if (data.success) {
          alert('✅ ' + (rutOriginal ? 'Usuario actualizado' : 'Usuario creado') + ' correctamente');
          cerrarModal();
          cargarUsuarios();
        } else {
          alert('❌ Error: ' + data.error);
        }
      })
      .catch(error => {
        console.error('[USUARIOS] Error:', error);
        alert('❌ Error al guardar usuario');
      })
      .finally(() => {
        btnGuardar.disabled = false;
        btnGuardar.textContent = 'Guardar';
      });
  }
  
  // Utilidades
  function obtenerColorRol(rol) {
    const colores = {
      'farmaceutico': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      'bodeguera': 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200',
      'supervisor': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
      'jefe': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      'administrador': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
    };
    const colorPorRol = colores[rol?.toLowerCase()] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
    console.log(`[USUARIOS] Color para rol "${rol}": ${colorPorRol}`);
    return colorPorRol;
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
  
  function formatearFecha(fecha) {
    if (!fecha) return '-';
    try {
      return new Date(fecha).toLocaleDateString('es-CL');
    } catch {
      return fecha;
    }
  }
  
  function validarRUT(rut) {
    return /^(\d{1,2}\.\d{3}\.\d{3}-\d|\d{7,8}-\d)$/.test(rut);
  }
  
  function validarEmail(email) {
    return /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email);
  }
  
  // Event Listeners
  if (btnCrear) {
    btnCrear.addEventListener('click', abrirModalCrear);
    console.log('[USUARIOS] Botón crear asignado');
  }
  
  if (btnCerrar) {
    btnCerrar.addEventListener('click', cerrarModal);
    console.log('[USUARIOS] Botón cerrar modal asignado');
  }
  
  if (btnCancelar) {
    btnCancelar.addEventListener('click', cerrarModal);
    console.log('[USUARIOS] Botón cancelar asignado');
  }
  
  if (btnGuardar) {
    btnGuardar.addEventListener('click', guardarUsuario);
    console.log('[USUARIOS] Botón guardar asignado');
  }
  
  if (form) {
    form.addEventListener('submit', guardarUsuario);
    console.log('[USUARIOS] Formulario asignado');
  }
  
  // Cerrar modal al hacer click en overlay
  if (modal) {
    modal.addEventListener('click', function(e) {
      if (e.target === modal) cerrarModal();
    });
  }
  
  // Cargar usuarios al iniciar
  cargarUsuarios();
  console.log('[USUARIOS] Inicialización completada');
});
