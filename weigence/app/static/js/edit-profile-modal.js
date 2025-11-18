/**
 * Script para manejar el modal de edición de perfil
 */

console.log('[EDIT-PROFILE-MODAL] Script externo cargado');

// Agregar evento al botón cuando esté listo
function setupEditProfileModal() {
  console.log('[EDIT-PROFILE-MODAL] Inicializando');

  const modal = document.getElementById('edit-profile-modal');
  const openBtn = document.getElementById('open-edit-modal');
  const closeBtn = document.getElementById('close-edit-modal');
  const cancelBtn = document.getElementById('cancel-edit-modal');
  const submitBtn = document.getElementById('submit-edit-modal');

  console.log('[EDIT-PROFILE-MODAL] Elementos:', {
    modal: !!modal,
    openBtn: !!openBtn,
    closeBtn: !!closeBtn,
    cancelBtn: !!cancelBtn,
    submitBtn: !!submitBtn
  });

  if (!modal) {
    console.error('[EDIT-PROFILE-MODAL] Modal no encontrado');
    return;
  }

  // Función para abrir el modal
  function abrirModal() {
    console.log('[EDIT-PROFILE-MODAL] Abriendo modal');
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  }

  // Función para cerrar el modal
  function cerrarModal() {
    console.log('[EDIT-PROFILE-MODAL] Cerrando modal');
    modal.classList.add('hidden');
    document.body.style.overflow = '';
  }

  // Abrir modal
  if (openBtn) {
    openBtn.addEventListener('click', abrirModal);
  }

  // Cerrar modal
  if (closeBtn) {
    closeBtn.addEventListener('click', cerrarModal);
  }
  if (cancelBtn) {
    cancelBtn.addEventListener('click', cerrarModal);
  }

  // Cerrar al hacer clic fuera
  modal.addEventListener('click', function(e) {
    if (e.target === modal) {
      cerrarModal();
    }
  });

  // Cerrar con Escape
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
      cerrarModal();
    }
  });

  // Validaciones de entrada
  const emailInput = document.getElementById('modal-email');
  const numeroInput = document.getElementById('modal-numero_celular');

  if (emailInput) {
    emailInput.addEventListener('blur', function() {
      const email = this.value.trim();
      const patron = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
      const emailError = document.getElementById('modal-email-error');
      if (email && !patron.test(email)) {
        if (emailError) {
          emailError.textContent = '❌ Correo inválido';
          emailError.classList.remove('hidden');
        }
      } else {
        if (emailError) emailError.classList.add('hidden');
      }
    });
  }

  if (numeroInput) {
    numeroInput.addEventListener('input', function() {
      const numero = this.value;
      const patron = /^(\+?)[\d\s\-\(\)]+$/;
      if (numero && !patron.test(numero)) {
        this.value = numero.replace(/[^\d\s\-\+\(\)]/g, '');
      }
    });
  }

  // Guardar cambios
  if (submitBtn) {
    submitBtn.addEventListener('click', async function() {
      console.log('[EDIT-PROFILE-MODAL] Guardando cambios');
      
      const nombreInput = document.getElementById('modal-nombre');
      const emailInput = document.getElementById('modal-email');
      const numeroInput = document.getElementById('modal-numero_celular');
      const statusMsg = document.getElementById('modal-status-message');

      const nombre = nombreInput ? nombreInput.value.trim() : '';
      const email = emailInput ? emailInput.value.trim() : '';
      const numero_celular = numeroInput ? numeroInput.value.trim() : '';

      // Validar
      if (!nombre) {
        if (statusMsg) {
          statusMsg.textContent = '❌ El nombre es requerido';
          statusMsg.classList.remove('hidden');
        }
        return;
      }

      // Enviar
      try {
        submitBtn.disabled = true;
        const originalText = submitBtn.textContent;
        submitBtn.textContent = '🔄 Guardando...';

        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

        const response = await fetch('/api/editar-perfil', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
          },
          credentials: 'same-origin',
          body: JSON.stringify({
            nombre,
            email,
            numero_celular
          })
        });

        const data = await response.json();

        if (data.success) {
          if (statusMsg) {
            statusMsg.textContent = '✅ Perfil actualizado';
            statusMsg.classList.remove('hidden');
          }
          setTimeout(() => {
            cerrarModal();
            location.reload();
          }, 2000);
        } else {
          if (statusMsg) {
            statusMsg.textContent = `❌ ${data.error || 'Error'}`;
            statusMsg.classList.remove('hidden');
          }
          submitBtn.disabled = false;
          submitBtn.textContent = originalText;
        }
      } catch (err) {
        console.error('[EDIT-PROFILE-MODAL] Error:', err);
        if (statusMsg) {
          statusMsg.textContent = '❌ Error de conexión';
          statusMsg.classList.remove('hidden');
        }
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
      }
    });
  }

  console.log('[EDIT-PROFILE-MODAL] Inicialización completada');
}

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', setupEditProfileModal);
} else {
  setupEditProfileModal();
}
