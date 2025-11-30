-- =====================================================
-- SCRIPT DE MIGRACIÓN: REACCIONES Y MENSAJES FIJADOS
-- Ejecutar en Supabase SQL Editor
-- =====================================================

-- 1. Crear tabla para reacciones a mensajes
CREATE TABLE IF NOT EXISTS chat_reacciones (
    id SERIAL PRIMARY KEY,
    mensaje_id INTEGER NOT NULL,
    usuario_id VARCHAR(20) NOT NULL,
    emoji VARCHAR(10) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    UNIQUE(mensaje_id, usuario_id)
);

-- 2. Agregar índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_chat_reacciones_mensaje ON chat_reacciones(mensaje_id);
CREATE INDEX IF NOT EXISTS idx_chat_reacciones_usuario ON chat_reacciones(usuario_id);

-- 3. Agregar columna para mensaje fijado en conversaciones
ALTER TABLE chat_conversaciones 
ADD COLUMN IF NOT EXISTS mensaje_fijado_id INTEGER;

-- 3b. Agregar columna para respuestas a mensajes
ALTER TABLE chat_mensajes 
ADD COLUMN IF NOT EXISTS reply_to INTEGER;

-- 4. Habilitar Row Level Security (RLS) para la tabla de reacciones
ALTER TABLE chat_reacciones ENABLE ROW LEVEL SECURITY;

-- 5. Crear políticas de seguridad para reacciones
CREATE POLICY "Usuarios pueden ver todas las reacciones" 
ON chat_reacciones FOR SELECT 
USING (true);

CREATE POLICY "Usuarios pueden agregar sus propias reacciones" 
ON chat_reacciones FOR INSERT 
WITH CHECK (true);

CREATE POLICY "Usuarios pueden actualizar sus propias reacciones" 
ON chat_reacciones FOR UPDATE 
USING (true);

CREATE POLICY "Usuarios pueden eliminar sus propias reacciones" 
ON chat_reacciones FOR DELETE 
USING (true);

-- 6. Comentarios para documentación
COMMENT ON TABLE chat_reacciones IS 'Reacciones de usuarios a mensajes del chat (❤️ 😂 😮 😔 👍)';
COMMENT ON COLUMN chat_reacciones.emoji IS 'Emoji de la reacción';
COMMENT ON COLUMN chat_conversaciones.mensaje_fijado_id IS 'ID del mensaje fijado en esta conversación';

-- ✅ Migración completada
