# 📧 Configurar Gmail para envío de correos

## Paso 1: Habilitar "Contraseña de aplicación" en tu cuenta de Gmail

### ⚠️ Requisito previo: Activar verificación en dos pasos

1. Abre: https://myaccount.google.com/security
2. En el menú izquierdo, haz clic en **"Seguridad"**
3. Desplázate a **"Verificación en dos pasos"**
4. Si **no está activada**:
   - Haz clic en **"Activar verificación en dos pasos"**
   - Sigue los pasos (necesitarás tu teléfono)
   - Confirma que esté activada

### ✅ Generar contraseña de aplicación

1. Una vez que 2FA está activo, ve a: https://myaccount.google.com/apppasswords
2. En **"Seleccionar la app"** → elige **"Correo"**
3. En **"Seleccionar el dispositivo"** → elige **"Windows" o "Otros"**
4. Google te mostrará una **contraseña de 16 caracteres** (con espacios)

Ejemplo: `aaaa bbbb cccc dddd`

## Paso 2: Copiar la contraseña en .env

1. Abre el archivo `.env` en la raíz del proyecto
2. Busca la línea: `MAIL_PASSWORD=aaaa bbbb cccc dddd`
3. **Reemplaza** `aaaa bbbb cccc dddd` con tu contraseña generada
4. **⚠️ Importante:** Mantén los espacios, NO los elimines
5. Guarda el archivo

**Ejemplo correcto:**
```env
MAIL_USERNAME=nelson.duarte@gmail.com
MAIL_PASSWORD=aaaa bbbb cccc dddd
MAIL_FROM=nelson.duarte@gmail.com
```

## Paso 3: Crear la tabla en Supabase

1. Ve a tu [Dashboard de Supabase](https://supabase.com/dashboard)
2. Selecciona tu proyecto
3. En el menú izquierdo, haz clic en **"SQL Editor"**
4. Copia todo el contenido de: `migrations/password_reset_tokens.sql`
5. Pégalo en el editor
6. Haz clic en **"Run"** (▶️)
7. Espera a que se cree la tabla (confirmación en verde ✅)

## Paso 4: Verificar que funciona

1. Abre una terminal en la carpeta del proyecto
2. Ejecuta: `python app.py`
3. Abre tu navegador en: http://localhost:5000
4. Haz clic en **"¿Olvidaste tu contraseña?"**
5. Ingresa tu email (ej: `nelson.duarte@gmail.com`)
6. Haz clic en **"Enviar enlace"**

### 📬 ¿Qué debería pasar?

- ✅ Deberías ver: *"Si el correo existe en nuestro sistema, recibirás un enlace..."*
- ✅ En **2-3 segundos**, recibirás un correo en tu bandeja
- ✅ El correo tiene un botón **"Restablecer Contraseña"**
- ❌ Si no recibes nada, revisa:
  - Carpeta **SPAM** o **Promociones**
  - Revisa los **logs en la consola** (deberías ver `[EMAIL] ✅ Correo enviado exitosamente`)

## Paso 5: Revisar los logs

En la consola deberías ver algo como:

```
[EMAIL] Conectando a smtp.gmail.com:587...
[EMAIL] ✅ Correo enviado exitosamente a: nelson.duarte@gmail.com
```

### Si ves errores:

**❌ Error: "MAIL_USERNAME o MAIL_PASSWORD no configuradas"**
- El `.env` no se cargó correctamente
- Asegúrate de que el archivo se llama exactamente `.env` (sin nada más)
- Reinicia `python app.py`

**❌ Error: "Error de autenticación SMTP"**
- La contraseña es incorrecta
- Cópiala nuevamente desde: https://myaccount.google.com/apppasswords
- Mantén los espacios
- Reinicia `python app.py`

**❌ Error: "Connection timeout"**
- Verifica que tu conexión a internet funciona
- Verifica que el firewall no bloquea puerto 587
- Intenta desde una red diferente

## Troubleshooting avanzado

### Ver variables de entorno cargadas

En Python, puedes verificar que se cargan correctamente:

```python
import os
from dotenv import load_dotenv
load_dotenv()

print(os.getenv("MAIL_USERNAME"))
print(os.getenv("MAIL_PASSWORD"))
print(os.getenv("MAIL_SERVER"))
```

### Enviar correo de prueba manualmente

```python
from app.email_utils import enviar_correo_recuperacion

# Prueba enviar a un email
resultado = enviar_correo_recuperacion("tu_email@gmail.com", "Test User")
print(f"Resultado: {resultado}")
```

### Verificar tabla en Supabase

1. Ve a Supabase Dashboard
2. En el menú izquierdo: **"Database"** → **"Tables"**
3. Deberías ver una tabla llamada **`password_reset_tokens`**
4. Puedes ver los tokens generados allí

---

## ✅ Resumen de pasos:

1. ✅ Activar 2FA en tu cuenta de Google
2. ✅ Generar contraseña de aplicación
3. ✅ Actualizar `.env` con la contraseña
4. ✅ Crear tabla en Supabase
5. ✅ Reiniciar la aplicación
6. ✅ Probar con "¿Olvidaste tu contraseña?"

**¿Listo?** Sigue estos pasos y debería funcionar. 🚀

Cualquier error, revisa los logs en consola (con prefijo `[EMAIL]`).
