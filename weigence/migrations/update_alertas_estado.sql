-- Migración: Actualizar alertas existentes de estantes de "pendiente" a "activo"
-- Fecha: 2025-12-07
-- Descripción: Cambia el estado de las alertas existentes para que aparezcan en notificaciones

-- Actualizar todas las alertas de estantes que están como "pendiente" a "activo"
UPDATE alertas 
SET estado = 'activo'
WHERE (titulo LIKE '%Estante%' OR titulo LIKE '%estante%')
  AND estado = 'pendiente';

-- Verificar el resultado
SELECT id, titulo, estado, fecha_creacion
FROM alertas
WHERE titulo LIKE '%Estante%'
ORDER BY fecha_creacion DESC
LIMIT 10;
