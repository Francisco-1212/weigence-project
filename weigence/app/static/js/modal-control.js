/**
 * SISTEMA GLOBAL DE CONTROL DE MODALES
 * Maneja la apertura/cierre de modales y el bloqueo de scroll
 */

document.addEventListener('DOMContentLoaded', () => {
  // Observador para detectar cuando se abren/cierran modales
  const observarModales = () => {
    const modales = document.querySelectorAll('.modal-overlay');
    
    modales.forEach(modal => {
      // Configurar MutationObserver para detectar cambios en la clase 'hidden'
      const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          if (mutation.attributeName === 'class') {
            const isHidden = modal.classList.contains('hidden');
            
            if (!isHidden) {
              // Modal abierto: bloquear scroll
              document.body.classList.add('modal-open');
            } else {
              // Modal cerrado: verificar si hay otros modales abiertos
              const hayModalAbierto = Array.from(document.querySelectorAll('.modal-overlay'))
                .some(m => !m.classList.contains('hidden'));
              
              if (!hayModalAbierto) {
                // No hay modales abiertos: restaurar scroll
                document.body.classList.remove('modal-open');
              }
            }
          }
        });
      });
      
      observer.observe(modal, { attributes: true });
      
      // Cerrar modal al hacer clic en el overlay (fondo)
      modal.addEventListener('click', (e) => {
        if (e.target === modal) {
          modal.classList.add('hidden');
          document.body.classList.remove('modal-open');
        }
      });
    });
  };
  
  // Cerrar modales con tecla ESC
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      const modalAbierto = document.querySelector('.modal-overlay:not(.hidden)');
      if (modalAbierto) {
        modalAbierto.classList.add('hidden');
        document.body.classList.remove('modal-open');
      }
    }
  });
  
  // Inicializar observadores
  observarModales();
  
  // Re-observar modales dinámicos (cargados después del DOM)
  setTimeout(observarModales, 1000);
});
