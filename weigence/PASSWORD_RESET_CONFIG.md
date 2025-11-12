# 📧 Configuración de Recuperación de Contraseña

## Pasos para habilitar el envío de correos de recuperación

### 1️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
# o específicamente:
pip install Flask-Mail
```

### 2️⃣ Crear tabla en Supabase

1. Ve a tu [Dashboard de Supabase](https://supabase.com/dashboard)
2. Abre el **SQL Editor**
3. Ejecuta el contenido del archivo: `migrations/password_reset_tokens.sql`

### 3️⃣ Configurar variables de entorno

#### Para Gmail (Recomendado):

1. Ve a: https://myaccount.google.com/apppasswords
2. Genera una contraseña de aplicación (necesitas tener 2FA activado)
3. Copia la contraseña generada
4. En la raíz del proyecto, crea un archivo `.env`:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_contraseña_de_aplicacion
MAIL_FROM=tu_email@gmail.com
BASE_URL=http://localhost:5000
```

#### Para Outlook/Office365:

```env
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USERNAME=tu_email@hotmail.com
MAIL_PASSWORD=tu_contraseña
MAIL_FROM=tu_email@hotmail.com
BASE_URL=http://localhost:5000
```

#### Para SendGrid (Alternativa):

```env
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USERNAME=apikey
MAIL_PASSWORD=SG.tu_api_key_aqui
MAIL_FROM=noreply@tudominio.com
BASE_URL=http://localhost:5000
```

### 4️⃣ Cómo funciona

**Flujo de recuperación:**

1. Usuario hace clic en "¿Olvidaste tu contraseña?"
2. Se abre un modal solicitando email
3. Envía el email al endpoint `/password-reset`
4. Backend:
   - Valida que el email exista en la BD
   - Genera un token seguro
   - Almacena en tabla `password_reset_tokens` (válido 1 hora)
   - Envía correo con enlace de recuperación
5. Usuario recibe correo con botón "Restablecer Contraseña"
6. Hace clic en enlace
7. Se valida el token y permite cambiar contraseña

### 5️⃣ Seguridad

✅ **Implementado:**
- Tokens seguros (urlib.tokens urlsafe 32 bytes)
- Expiración de 1 hora
- Tokens de un solo uso
- Mensajes genéricos (no revela si email existe)
- HTTPONLY cookies
- CSRF protection

### 6️⃣ Pruebas

**Desarrollo local:**

```bash
python app.py
```

1. Ve a http://localhost:5000
2. Haz clic en "¿Olvidaste tu contraseña?"
3. Ingresa un email de usuario registrado
4. Verifica en la bandeja de correos

**Producción:**

Cambiar en `.env`:
```env
BASE_URL=https://tudominio.com
SESSION_COOKIE_SECURE=True
```

### 7️⃣ Solución de problemas

**Error: `MAIL_USERNAME o MAIL_PASSWORD no configuradas`**
- Verificar que `.env` existe en la raíz del proyecto
- Verificar que las variables están correctamente escritas

**Error: `Error de autenticación SMTP`**
- Para Gmail: Verificar que usas contraseña de aplicación, no contraseña de cuenta
- Verificar credenciales en `.env`
- Activar "Aplicaciones menos seguras" si es necesario (no recomendado)

**Email no llega:**
- Verificar carpeta de spam/correo no deseado
- Verificar que el MAIL_FROM sea correcto
- Revisar logs en consola (`[EMAIL]` prefix)

**Token expirado:**
- Los tokens expiran después de 1 hora
- Usuario debe hacer clic en el enlace antes

### 8️⃣ Próximas mejoras (Opcional)

- [ ] Página web para cambiar contraseña (en lugar de solo email)
- [ ] Reenvío de correo si no lo recibe
- [ ] Límite de intentos de recuperación
- [ ] Notificación en dashboard cuando se cambia contraseña
- [ ] Dos factores de autenticación (2FA)

---

**¿Preguntas?** Revisa los logs con prefix `[EMAIL]` para debugging.
