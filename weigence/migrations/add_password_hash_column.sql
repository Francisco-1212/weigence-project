-- ============================================================
-- MIGRACIÓN: Agregar columna password_hash a tabla usuarios
-- ============================================================
-- 
-- INSTRUCCIONES:
-- 1. Ir a: https://supabase.com/dashboard/project/[TU_PROJECT_ID]/editor
-- 2. Copiar y ejecutar este SQL
-- 3. Volver a ejecutar: python scripts/migrar_passwords.py
--
-- ============================================================

-- Agregar columna password_hash (permitir NULL temporalmente)
ALTER TABLE usuarios 
ADD COLUMN IF NOT EXISTS password_hash TEXT;

-- Crear índice para mejorar performance en login
CREATE INDEX IF NOT EXISTS idx_usuarios_password_hash 
ON usuarios(password_hash);

-- Agregar comentario descriptivo
COMMENT ON COLUMN usuarios.password_hash IS 
'Hash bcrypt de la contraseña (12 rounds). Reemplaza el campo Contraseña.';

-- ============================================================
-- VERIFICACIÓN
-- ============================================================
-- Ejecuta esto para verificar que la columna fue creada:
-- SELECT column_name, data_type, is_nullable 
-- FROM information_schema.columns 
-- WHERE table_name = 'usuarios' AND column_name = 'password_hash';
-- ============================================================

-- NOTA: Después de migrar todas las contraseñas, se recomienda:
-- 1. Hacer NOT NULL la columna password_hash
-- 2. Eliminar la columna Contraseña antigua
-- 3. Usar este SQL (ejecutar DESPUÉS de la migración):
/*
ALTER TABLE usuarios 
ALTER COLUMN password_hash SET NOT NULL;

ALTER TABLE usuarios 
DROP COLUMN IF EXISTS "Contraseña";
*/
