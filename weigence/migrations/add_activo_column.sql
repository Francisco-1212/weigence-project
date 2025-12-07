-- Migración: Agregar columna 'activo' para eliminación lógica
-- Fecha: 2025-12-07
-- Descripción: Permite marcar productos como inactivos sin eliminarlos físicamente,
--              preservando el historial de ventas

-- Agregar columna activo (por defecto TRUE para productos existentes)
ALTER TABLE productos 
ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT TRUE;

-- Actualizar productos existentes para que estén activos
UPDATE productos 
SET activo = TRUE 
WHERE activo IS NULL;

-- Crear índice para mejorar consultas de productos activos
CREATE INDEX IF NOT EXISTS idx_productos_activo ON productos(activo);

-- Comentario en la columna
COMMENT ON COLUMN productos.activo IS 'Indica si el producto está activo (TRUE) o fue eliminado lógicamente (FALSE)';
