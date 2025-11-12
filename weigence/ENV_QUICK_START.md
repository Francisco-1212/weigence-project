# ⚙️ Guía Rápida: Funcionamiento del .env

## 📋 Tu situación actual

✅ Tienes `.env` con:
- `SUPABASE_KEY` y `SUPABASE_URL` (ya configurados)
- Variables de email (pero todavía con placeholder)

## 🎯 Lo que necesitas hacer

### Paso 1: Configurar Gmail (5 minutos)

**Opción A: Si tienes Gmail**

1. Ve a: https://myaccount.google.com/apppasswords
   - (Necesitas tener 2FA activado. Si no, ve a Security primero)
2. Selecciona:
   - App: **Correo**
   - Dispositivo: **Windows**
3. Google te dará una contraseña de 16 caracteres: `aaaa bbbb cccc dddd`
4. Copia esa contraseña en tu `.env`:
   ```env
   MAIL_PASSWORD=aaaa bbbb cccc dddd
   ```
   (Sin cambiar los espacios)

**Opción B: Si no tienes Gmail**

- **Outlook**: `MAIL_SERVER=smtp-mail.outlook.com`
- **SendGrid**: `MAIL_SERVER=smtp.sendgrid.net`
- **Otro**: Usa tu proveedor de email

### Paso 2: Actualizar .env

Edita el archivo `.env` en la raíz:

```env
# ========== CONFIGURACIÓN DE CORREOS ==========
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=nelson.duarte@gmail.com        # ← Tu email de Gmail
MAIL_PASSWORD=aaaa bbbb cccc dddd             # ← Contraseña generada
MAIL_FROM=nelson.duarte@gmail.com             # ← Mismo email
BASE_URL=http://localhost:5000
```

### Paso 3: Crear tabla en Supabase

1. Ve a: https://supabase.com/dashboard
2. Abre tu proyecto
3. Click en **SQL Editor**
4. Copia-pega el contenido de: `migrations/password_reset_tokens.sql`
5. Click en **Run** (▶️)
6. Espera confirmación ✅

### Paso 4: Verificar todo

En terminal, ejecuta:
```bash
python test_email.py
```

Esto verificará:
- ✅ Archivo `.env` existe
- ✅ Variables están configuradas
- ✅ Tabla existe en Supabase
- ✅ Conexión SMTP funciona
- ✅ Autenticación exitosa

### Paso 5: Probar con la app

```bash
python app.py
```

Luego:
1. Ve a http://localhost:5000
2. Haz clic en **"¿Olvidaste tu contraseña?"**
3. Ingresa tu email
4. Deberías recibir un correo en 2-3 segundos

## 🔧 Variables del .env explicadas

| Variable | Qué es | Ejemplo |
|----------|--------|---------|
| `MAIL_SERVER` | Servidor SMTP | `smtp.gmail.com` |
| `MAIL_PORT` | Puerto SMTP | `587` |
| `MAIL_USERNAME` | Tu email | `nelson.duarte@gmail.com` |
| `MAIL_PASSWORD` | Contraseña de aplicación | `aaaa bbbb cccc dddd` |
| `MAIL_FROM` | Email que aparece como remitente | Igual a USERNAME |
| `BASE_URL` | URL base para enlaces de reset | `http://localhost:5000` |

## ❌ Errores comunes y soluciones

| Error | Causa | Solución |
|-------|-------|----------|
| `MAIL_PASSWORD no configurada` | `.env` no se cargó | Reinicia `python app.py` |
| `Error de autenticación SMTP` | Contraseña incorrecta | Genera nueva en apppasswords |
| `Connection timeout` | Firewall bloquea puerto 587 | Usa VPN o red diferente |
| `Email no llega` | Filtrado por spam | Revisa carpeta SPAM |

## ✅ Checklist

- [ ] Activé 2FA en mi cuenta de Google
- [ ] Generé contraseña de aplicación
- [ ] Copié la contraseña en `.env` (con espacios)
- [ ] Ejecuté SQL en Supabase
- [ ] Ejecuté `python test_email.py` (sin errores)
- [ ] Probé con "¿Olvidaste tu contraseña?"
- [ ] Recibí correo en mi bandeja

## 📞 ¿Qué hacer si algo falla?

1. **Ejecuta el test:**
   ```bash
   python test_email.py
   ```

2. **Revisa los logs** en la consola (busca `[EMAIL]`)

3. **Comprueba:**
   - ¿Tienes conexión a internet?
   - ¿La contraseña de Gmail es la de "apppasswords" no la normal?
   - ¿Copiaste toda la contraseña con espacios?
   - ¿El `.env` está en la raíz (mismo nivel que `app.py`)?

4. **Si sigue sin funcionar:**
   - Revisa `PASSWORD_RESET_CONFIG.md` para más detalles
   - O revisa `CONFIGURAR_GMAIL.md` para paso a paso

---

**¿Listo? Comienza con el Paso 1.** 🚀
