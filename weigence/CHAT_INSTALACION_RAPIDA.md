# 🚀 Instalación Rápida del Sistema de Chat

## Paso 1: Crear las tablas en Supabase

1. Ve a tu proyecto en Supabase: https://supabase.com/dashboard/project/_/sql

2. Copia y ejecuta el siguiente SQL:

```sql
-- Tabla de conversaciones de chat
CREATE TABLE IF NOT EXISTS conversaciones_chat (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(255),
    es_grupal BOOLEAN DEFAULT false,
    creado_por INTEGER REFERENCES usuarios(idusuario),
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ultima_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de participantes en conversaciones
CREATE TABLE IF NOT EXISTS participantes_chat (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversacion_id UUID REFERENCES conversaciones_chat(id) ON DELETE CASCADE,
    usuario_id INTEGER REFERENCES usuarios(idusuario) ON DELETE CASCADE,
    fecha_ingreso TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ultimo_mensaje_leido UUID,
    UNIQUE(conversacion_id, usuario_id)
);

-- Tabla de mensajes
CREATE TABLE IF NOT EXISTS mensajes_chat (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversacion_id UUID REFERENCES conversaciones_chat(id) ON DELETE CASCADE,
    usuario_id INTEGER REFERENCES usuarios(idusuario) ON DELETE CASCADE,
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
DROP TRIGGER IF EXISTS trigger_actualizar_conversacion ON mensajes_chat;
CREATE TRIGGER trigger_actualizar_conversacion
AFTER INSERT ON mensajes_chat
FOR EACH ROW
EXECUTE FUNCTION actualizar_conversacion_timestamp();
```

3. Haz clic en "Run" para ejecutar

## Paso 2: Verificar instalación

Ejecuta este comando para verificar que las tablas se crearon:

```bash
python -c "from app.app_config import get_supabase; sb = get_supabase(); print('✅ Conexión exitosa'); print('Tablas:', sb.table('conversaciones_chat').select('*').limit(0).execute())"
```

## Paso 3: Acceder al chat

1. Inicia la aplicación:
   ```bash
   python app.py
   ```

2. Navega a: http://localhost:5000/chat

## Paso 4: Probar el chat

1. Inicia sesión con dos usuarios diferentes en dos navegadores
2. Crea una nueva conversación desde uno de ellos
3. Envía mensajes y verifica que se actualicen en ambos lados

## ✅ ¡Listo!

El sistema de chat está completamente instalado y funcionando.

Ver documentación completa en: `CHAT_DOCUMENTACION.md`
