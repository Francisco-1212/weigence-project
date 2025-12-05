/**
 * Sistema centralizado de registro de errores en auditoría
 * Envía errores críticos del frontend a la base de datos de auditoría
 */

class ErrorLogger {
  constructor() {
    this.endpoint = '/api/log_error';
    this.enabled = true;
  }

  /**
   * Registra un error en la consola de auditoría
   * @param {string} message - Mensaje principal del error
   * @param {Object} options - Opciones adicionales
   * @param {string} options.detail - Detalle adicional del error
   * @param {string} options.level - Nivel: 'error', 'warning', 'critical'
   * @param {string} options.module - Módulo donde ocurrió: 'ventas', 'usuarios', etc.
   * @param {Error} options.error - Objeto Error de JavaScript
   * @param {boolean} options.silent - Si true, no muestra en consola del navegador
   */
  async log(message, options = {}) {
    const {
      detail = '',
      level = 'error',
      module = 'frontend',
      error = null,
      silent = false
    } = options;

    // Construir detalle completo
    let fullDetail = detail;
    if (error) {
      fullDetail += ` | ${error.message}`;
      if (error.stack && level === 'critical') {
        fullDetail += ` | Stack: ${error.stack.substring(0, 200)}`;
      }
    }

    // Mostrar en consola del navegador si no es silent
    if (!silent) {
      const consoleMethod = level === 'critical' ? 'error' : level === 'warning' ? 'warn' : 'error';
      console[consoleMethod](`[${module.toUpperCase()}] ${message}`, fullDetail);
    }

    // Enviar a auditoría si está habilitado
    if (!this.enabled) return;

    try {
      const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
      
      await fetch(this.endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
          message: `[${module}] ${message}`,
          detail: fullDetail,
          level: level
        })
      });
    } catch (e) {
      // Error al enviar a auditoría, solo log local
      if (!silent) {
        console.warn('No se pudo registrar error en auditoría:', e);
      }
    }
  }

  /**
   * Atajos para niveles específicos
   */
  error(message, module, detail = '', error = null) {
    return this.log(message, { detail, level: 'error', module, error });
  }

  warning(message, module, detail = '', error = null) {
    return this.log(message, { detail, level: 'warning', module, error });
  }

  critical(message, module, detail = '', error = null) {
    return this.log(message, { detail, level: 'critical', module, error });
  }

  /**
   * Desactiva el envío a auditoría (útil para desarrollo)
   */
  disable() {
    this.enabled = false;
  }

  /**
   * Activa el envío a auditoría
   */
  enable() {
    this.enabled = true;
  }
}

// Instancia global
window.errorLogger = new ErrorLogger();
