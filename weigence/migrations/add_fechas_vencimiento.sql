-- Migración: Agregar fechas de elaboración y vencimiento a productos
-- Ejecutar en Supabase SQL Editor

-- 1. Agregar columnas a la tabla productos
ALTER TABLE productos 
ADD COLUMN IF NOT EXISTS fecha_elaboracion DATE,
ADD COLUMN IF NOT EXISTS fecha_vencimiento DATE;

-- 2. Crear índice para consultas rápidas de productos próximos a vencer
CREATE INDEX IF NOT EXISTS idx_productos_fecha_vencimiento 
ON productos(fecha_vencimiento) 
WHERE fecha_vencimiento IS NOT NULL;

-- 3. Comentarios para documentación
COMMENT ON COLUMN productos.fecha_elaboracion IS 'Fecha de elaboración/fabricación del producto';
COMMENT ON COLUMN productos.fecha_vencimiento IS 'Fecha de vencimiento/caducidad del producto';

-- 4. Vista para productos próximos a vencer (30 días)
CREATE OR REPLACE VIEW productos_proximos_vencer AS
SELECT 
    idproducto,
    nombre,
    categoria,
    stock,
    fecha_elaboracion,
    fecha_vencimiento,
    (fecha_vencimiento - CURRENT_DATE) as dias_restantes
FROM productos
WHERE fecha_vencimiento IS NOT NULL
  AND fecha_vencimiento >= CURRENT_DATE
  AND fecha_vencimiento <= (CURRENT_DATE + INTERVAL '30 days')
ORDER BY fecha_vencimiento ASC;

-- 5. Vista para productos vencidos
CREATE OR REPLACE VIEW productos_vencidos AS
SELECT 
    idproducto,
    nombre,
    categoria,
    stock,
    fecha_elaboracion,
    fecha_vencimiento,
    (CURRENT_DATE - fecha_vencimiento) as dias_vencido
FROM productos
WHERE fecha_vencimiento IS NOT NULL
  AND fecha_vencimiento < CURRENT_DATE
ORDER BY fecha_vencimiento DESC;
