-- Tabla de conversaciones de chat
CREATE TABLE IF NOT EXISTS conversaciones_chat (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(255),
    es_grupal BOOLEAN DEFAULT false,
    creado_por VARCHAR(20) REFERENCES usuarios(rut_usuario),
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ultima_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de participantes en conversaciones
CREATE TABLE IF NOT EXISTS participantes_chat (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversacion_id UUID REFERENCES conversaciones_chat(id) ON DELETE CASCADE,
    usuario_id VARCHAR(20) REFERENCES usuarios(rut_usuario) ON DELETE CASCADE,
    fecha_ingreso TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ultimo_mensaje_leido UUID,
    UNIQUE(conversacion_id, usuario_id)
);

-- Tabla de mensajes
CREATE TABLE IF NOT EXISTS mensajes_chat (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversacion_id UUID REFERENCES conversaciones_chat(id) ON DELETE CASCADE,
    usuario_id VARCHAR(20) REFERENCES usuarios(rut_usuario) ON DELETE CASCADE,
    contenido TEXT NOT NULL,
    fecha_envio TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    editado BOOLEAN DEFAULT false,
    eliminado BOOLEAN DEFAULT false
);

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_mensajes_conversacion ON mensajes_chat(conversacion_id, fecha_envio DESC);
CREATE INDEX IF NOT EXISTS idx_participantes_conversacion ON participantes_chat(conversacion_id);
CREATE INDEX IF NOT EXISTS idx_participantes_usuario ON participantes_chat(usuario_id);
CREATE INDEX IF NOT EXISTS idx_conversaciones_actualizacion ON conversaciones_chat(ultima_actualizacion DESC);

-- Función para actualizar última actualización de conversación
CREATE OR REPLACE FUNCTION actualizar_conversacion_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversaciones_chat 
    SET ultima_actualizacion = NOW() 
    WHERE id = NEW.conversacion_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para actualizar timestamp al insertar mensaje
CREATE TRIGGER trigger_actualizar_conversacion
AFTER INSERT ON mensajes_chat
FOR EACH ROW
EXECUTE FUNCTION actualizar_conversacion_timestamp();

-- Comentarios de documentación
COMMENT ON TABLE conversaciones_chat IS 'Almacena las conversaciones individuales y grupales';
COMMENT ON TABLE participantes_chat IS 'Relaciona usuarios con conversaciones';
COMMENT ON TABLE mensajes_chat IS 'Almacena todos los mensajes del chat';
