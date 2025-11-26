// ===============================================================
//  MÓDULO: AUDIT API
//  Maneja todas las llamadas fetch a los endpoints de auditoría
// ===============================================================

const API_ENDPOINTS = {
  LOGS: "/api/auditoria/logs",
  LIVE: "/api/auditoria/live-trail",
  EXPORT: "/api/auditoria/export",
  RECALIBRAR: "/api/auditoria/recalibrar",
  USUARIOS: "/api/usuarios"
};

/**
 * Obtiene logs de auditoría con filtros y paginación
 * @param {Object} filtros - Filtros a aplicar
 * @param {number} horasRango - Horas hacia atrás para cargar
 * @returns {Promise<Object>} Respuesta con logs y metadatos
 */
export async function fetchLogs(filtros = {}, horasRango = 24) {
  const params = new URLSearchParams(filtros);
  params.set('horas', horasRango);
  
  // Ajustar límite según rango temporal
  let limit = 200; // Default para 24h
  if (horasRango >= 720) limit = 1000; // Mes
  else if (horasRango >= 168) limit = 500; // Semana
  params.set('limit', limit);
  
  const url = `${API_ENDPOINTS.LOGS}?${params.toString()}`;
  const startTime = Date.now();
  
  const res = await fetch(url);
  
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  }
  
  const data = await res.json();
  const loadTime = Date.now() - startTime;
  
  if (!data.ok) {
    throw new Error(data.error || "Error desconocido en backend");
  }
  
  return {
    logs: data.logs || [],
    meta: data.meta,
    loadTime
  };
}

/**
 * Exporta logs en el formato especificado
 * @param {string} formato - Formato de exportación (csv, zip, pdf)
 * @param {Object} filtros - Filtros aplicados
 * @returns {Promise<Blob>} Archivo para descarga
 */
export async function exportLogs(formato, filtros = {}) {
  const payload = {
    formato,
    filtros,
    limit: 600
  };

  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

  const res = await fetch(API_ENDPOINTS.EXPORT, {
    method: "POST",
    headers: { 
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken
    },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    throw new Error(`Error exportando: ${res.status}`);
  }

  return await res.blob();
}

/**
 * Obtiene lista completa de usuarios del sistema
 * @returns {Promise<Array>} Lista de usuarios
 */
export async function fetchUsuarios() {
  const response = await fetch(API_ENDPOINTS.USUARIOS);
  const data = await response.json();
  
  if (!data.success) {
    throw new Error(data.error || "Error obteniendo usuarios");
  }
  
  return data.data || [];
}

/**
 * Recalibra sensores del sistema (DEPRECADO)
 * @returns {Promise<Object>} Respuesta de recalibración
 */
export async function recalibrarSensores() {
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

  const res = await fetch(API_ENDPOINTS.RECALIBRAR, {
    method: "POST",
    headers: { 
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken
    },
    body: JSON.stringify({ detalle: "Recalibración solicitada desde UI" })
  });

  const data = await res.json();
  return data;
}

export { API_ENDPOINTS };
