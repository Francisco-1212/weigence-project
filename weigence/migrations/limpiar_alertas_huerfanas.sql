-- Limpieza manual de alertas de productos inexistentes
-- Fecha: 2025-12-07
-- Descripción: Resuelve alertas de productos que ya no existen en la tabla productos

-- Opción 1: Resolver alertas de productos específicos (como Aspirina)
UPDATE alertas 
SET estado = 'resuelto'
WHERE titulo LIKE '%Aspirina%'
  AND estado IN ('pendiente', 'activo');

-- Opción 2: Resolver TODAS las alertas de productos que ya no existen
UPDATE alertas 
SET estado = 'resuelto'
WHERE idproducto IS NOT NULL
  AND estado IN ('pendiente', 'activo')
  AND idproducto NOT IN (
    SELECT idproducto 
    FROM productos 
    WHERE activo = true
  );

-- Opción 3: Si no tienes columna 'activo', usa esta consulta
UPDATE alertas 
SET estado = 'resuelto'
WHERE idproducto IS NOT NULL
  AND estado IN ('pendiente', 'activo')
  AND idproducto NOT IN (
    SELECT idproducto 
    FROM productos
  );

-- Verificar alertas resueltas
SELECT id, titulo, estado, idproducto, fecha_creacion
FROM alertas
WHERE titulo LIKE '%Aspirina%'
ORDER BY fecha_creacion DESC;
