-- Tabla para almacenar tokens de recuperación de contraseña
-- Ejecutar esta query en la consola de Supabase: https://supabase.com/dashboard

CREATE TABLE IF NOT EXISTS password_reset_tokens (
  id BIGSERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL,
  token VARCHAR(255) NOT NULL UNIQUE,
  created_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP NOT NULL,
  usado BOOLEAN DEFAULT FALSE,
  created_at_user TIMESTAMP,
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices para mejor rendimiento
CREATE INDEX idx_email ON password_reset_tokens(email);
CREATE INDEX idx_token ON password_reset_tokens(token);
CREATE INDEX idx_expires_at ON password_reset_tokens(expires_at);

-- Política de seguridad (opcional, para RLS)
ALTER TABLE password_reset_tokens ENABLE ROW LEVEL SECURITY;

-- Comentario
COMMENT ON TABLE password_reset_tokens IS 'Almacena tokens temporales para recuperación de contraseña';
