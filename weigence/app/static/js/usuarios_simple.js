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
  
  // Variable global para usuarios conectados
  let usuariosConectados = [];
  
  // Función: Cargar usuarios conectados
  function cargarUsuariosConectados(forzarRecarga = true) {
    const ahora = new Date().toLocaleTimeString();
    console.log(`[USUARIOS-CONECTADOS] 🔄 [${ahora}] Solicitando lista de usuarios conectados...`);
    
    fetch('/api/usuarios/conectados')
      .then(response => {
        console.log('[USUARIOS-CONECTADOS] 📡 Respuesta recibida, status:', response.status);
        return response.json();
      })
      .then(data => {
        if (data.success) {
          const anteriorConectados = usuariosConectados.length;
          const anteriorRuts = [...usuariosConectados];
          usuariosConectados = data.conectados || [];
          
          console.log(`[USUARIOS-CONECTADOS] ✓ [${ahora}] Actualización exitosa:`, {
            total: data.total,
            anterior: anteriorConectados,
            actual: usuariosConectados.length,
            conectados: usuariosConectados,
            detalles: data.detalles
          });
          
          // Detectar cambios en la lista de usuarios
          const huboChangios = usuariosConectados.length !== anteriorConectados ||
                             JSON.stringify(usuariosConectados.sort()) !== JSON.stringify(anteriorRuts.sort());
          
          if (huboChangios) {
            console.log(`[USUARIOS-CONECTADOS] 🔔 Cambio detectado: ${anteriorConectados} → ${usuariosConectados.length}`);
          }
          
          // Recargar la tabla para actualizar estados solo si hubo cambios o es forzado
          if (huboChangios || forzarRecarga) {
            cargarUsuarios();
          }
        } else {
          console.error('[USUARIOS-CONECTADOS] ❌ Error en respuesta:', data);
        }
      })
      .catch(error => {
        console.error('[USUARIOS-CONECTADOS] ❌ Error de red:', error);
      });
  }
  
  // Función: Enviar heartbeat (desde página de usuarios)
  function enviarHeartbeat() {
    const ahora = new Date().toLocaleTimeString();
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || '';
    fetch('/api/usuarios/heartbeat', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      }
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          console.log(`[USUARIOS-HEARTBEAT] ✓ [${ahora}] Heartbeat local enviado - Total conectados: ${data.total_conectados}`);
        }
      })
      .catch(error => {
        console.error('[USUARIOS-HEARTBEAT] ❌ Error:', error);
      });
  }
  
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
              <td colspan="8" class="px-6 py-4 text-center text-red-500">
                Error: ${data.error}
              </td>
            </tr>
          `;
          actualizarEstadisticas([], []);
          return;
        }
        
        if (!data.data || data.data.length === 0) {
          tablaBody.innerHTML = `
            <tr>
              <td colspan="8" class="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
                <div class="flex flex-col items-center gap-3">
                  <span class="material-symbols-outlined text-5xl text-gray-300 dark:text-gray-600">group_off</span>
                  <p class="font-medium">No hay usuarios registrados</p>
                </div>
              </td>
            </tr>
          `;
          actualizarEstadisticas([], []);
          return;
        }
        
        // Filtrar usuarios activos basándose en la lista de conectados
        const usuariosActivos = data.data.filter(u => 
          usuariosConectados.includes(u.rut_usuario)
        );
        
        console.log('[USUARIOS] 📊 Estadísticas:', {
          totalUsuarios: data.data.length,
          conectados: usuariosConectados.length,
          listaConectados: usuariosConectados,
          usuariosActivos: usuariosActivos.map(u => u.rut_usuario)
        });
        
        // Actualizar estadísticas
        actualizarEstadisticas(data.data, usuariosActivos);
        
        // Mostrar usuarios
        tablaBody.innerHTML = data.data.map(usuario => {
          const rolMinuscula = usuario.rol?.toLowerCase() || 'usuario';
          const estaConectado = usuariosConectados.includes(usuario.rut_usuario);
          
          return `
          <tr class="hover:bg-neutral-50 dark:hover:bg-neutral-700/50 transition-colors">
            <td class="px-3 sm:px-6 py-3 sm:py-4 text-sm text-neutral-900 dark:text-neutral-100">
              <div class="font-medium">${usuario.nombre}</div>
              <div class="text-xs text-neutral-500 dark:text-neutral-400 sm:hidden">${usuario.rut_usuario}</div>
            </td>
            <td class="px-3 sm:px-6 py-3 sm:py-4 text-xs sm:text-sm text-neutral-600 dark:text-neutral-400 hidden sm:table-cell">${usuario.correo}</td>
            <td class="px-3 sm:px-6 py-3 sm:py-4 text-sm">
              <span class="px-2 sm:px-3 py-0.5 sm:py-1 rounded-full text-xs font-medium ${obtenerColorRol(rolMinuscula)}">
                ${formatearRol(rolMinuscula)}
              </span>
            </td>
            <td class="px-3 sm:px-6 py-3 sm:py-4 text-sm hidden md:table-cell">
              <span class="inline-flex items-center px-2 sm:px-2.5 py-0.5 rounded-full text-xs font-medium ${estaConectado ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200' : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'}">
                <span class="w-1.5 h-1.5 rounded-full ${estaConectado ? 'bg-green-600 dark:bg-green-400 animate-pulse' : 'bg-gray-600 dark:bg-gray-400'} mr-1"></span>
                ${estaConectado ? 'Conectado' : 'Desconectado'}
              </span>
            </td>
            <td class="px-3 sm:px-6 py-3 sm:py-4 text-right">
              <button onclick="editarUsuario('${usuario.rut_usuario}')" class="inline-flex items-center gap-1 px-2 sm:px-3 py-1 sm:py-1.5 bg-neutral-200 dark:bg-neutral-700 border border-neutral-300 dark:border-neutral-600 text-neutral-700 dark:text-neutral-200 hover:bg-neutral-300 dark:hover:bg-neutral-600 text-xs font-medium rounded-lg transition-colors">
                <span class="material-symbols-outlined text-sm">edit</span>
                <span class="hidden sm:inline">Editar</span>
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
            <td colspan="8" class="px-6 py-4 text-center text-red-500">
              Error al cargar usuarios: ${error.message}
            </td>
          </tr>
        `;
        actualizarEstadisticas([], []);
      });
  }
  
  // Función: Actualizar estadísticas
  function actualizarEstadisticas(todosLosUsuarios, usuariosConectados) {
    const total = todosLosUsuarios.length;
    const conectados = usuariosConectados.length;
    const desconectados = total - conectados;
    // Contar solo usuarios con rol 'administrador'
    const admins = todosLosUsuarios.filter(u => 
      u.rol?.toLowerCase() === 'administrador'
    ).length;
    
    // Actualizar contadores
    document.getElementById('total-usuarios').textContent = total;
    document.getElementById('usuarios-activos').textContent = conectados;
    document.getElementById('usuarios-inactivos').textContent = desconectados;
    document.getElementById('usuarios-admin').textContent = admins;
    document.getElementById('usuarios-count-badge').textContent = total;
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
        if (window.errorLogger) {
          window.errorLogger.error('Error al cargar usuario', 'usuarios', error.message, error);
        }
        console.error('[USUARIOS] Error:', error);
        alert('Error al cargar usuario: ' + error.message);
      });
  };
  
  // Función: Eliminar usuario (DESHABILITADA - botón eliminado de la interfaz)
  // window.eliminarUsuario = function(rut, nombre) {
  //   if (!confirm(`¿Estás seguro de que deseas eliminar a ${nombre}?`)) {
  //     return;
  //   }
  //   
  //   console.log('[USUARIOS] Eliminando usuario:', rut);
  //   
  //   fetch(`/api/usuarios/${rut}`, {
  //     method: 'DELETE',
  //     headers: { 'Content-Type': 'application/json' }
  //   })
  //     .then(response => response.json())
  //     .then(data => {
  //       if (data.success) {
  //         console.log('[USUARIOS] Usuario eliminado');
  //         alert('✅ Usuario eliminado correctamente');
  //         cargarUsuarios();
  //       } else {
  //         alert('❌ Error: ' + data.error);
  //       }
  //     })
  //     .catch(error => {
  //       console.error('[USUARIOS] Error:', error);
  //       alert('❌ Error al eliminar usuario');
  //     });
  // };
  
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
        if (window.errorLogger) {
          window.errorLogger.critical('Error al guardar usuario', 'usuarios', '', error);
        }
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
      'operador': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      'supervisor': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
      'administrador': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
    };
    const colorPorRol = colores[rol?.toLowerCase()] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
    console.log(`[USUARIOS] Color para rol "${rol}": ${colorPorRol}`);
    return colorPorRol;
  }
  
  function formatearRol(rol) {
    const roles = {
      'operador': 'Operador',
      'supervisor': 'Supervisor',
      'administrador': 'Administrador'
    };
    return roles[rol] || rol.charAt(0).toUpperCase() + rol.slice(1);
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
  
  // Cargar usuarios al iniciar - con espera para asegurar que el heartbeat global se registre primero
  console.log('[USUARIOS] Esperando 800ms para asegurar registro de heartbeat global...');
  setTimeout(() => {
    console.log('[USUARIOS] Iniciando carga de datos...');
    cargarUsuariosConectados(true); // Forzar recarga inicial
  }, 800);
  
  // Enviar heartbeat cada 10 segundos (más frecuente)
  enviarHeartbeat(); // Enviar inmediatamente
  setInterval(enviarHeartbeat, 10000); // Cada 10 segundos
  
  // Actualizar usuarios conectados cada 3 segundos para detección en tiempo real
  setInterval(() => cargarUsuariosConectados(false), 3000); // No forzar recarga cada vez, solo si hay cambios
  
  console.log('[USUARIOS] Inicialización completada - Heartbeat: 10s, Actualización: 3s');
});
