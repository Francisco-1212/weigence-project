# 🔒 GUÍA DE SEGURIDAD - Weigence Inventory

## 📋 Índice de Mejoras Implementadas

### ✅ COMPLETADO - Mejoras de Seguridad

1. **Hash de Contraseñas con bcrypt** ✓
2. **Protección CSRF** ✓  
3. **Rate Limiting** ✓
4. **Logging Centralizado** ✓
5. **Configuración Segura** ✓
6. **Validación de Inputs** ✓
7. **Gestión de Variables de Entorno** ✓

---

## 🚨 PASOS CRÍTICOS DESPUÉS DE ACTUALIZAR

### 1. Instalar Nuevas Dependencias

```bash
pip install -r app/requirements.txt
```

Nuevas librerías agregadas:
- `bcrypt` - Hash de contraseñas
- `Flask-WTF` - Protección CSRF
- `Flask-Limiter` - Rate limiting

### 2. Configurar SECRET_KEY

**IMPORTANTE:** La aplicación ya NO funcionará sin SECRET_KEY configurada.

```bash
# Generar una clave secreta
python -c "import secrets; print(secrets.token_hex(32))"
```

Agregar al archivo `.env`:
```env
SECRET_KEY=tu_clave_generada_aqui
```

### 3. Verificar que .env NO esté en Git

```bash
# Verificar
git status

# Si .env aparece, eliminarlo del repositorio:
git rm --cached .env
git commit -m "Remover .env del repositorio"
git push
```

### 4. MIGRAR CONTRASEÑAS EXISTENTES

**CRÍTICO:** Si ya tienes usuarios en la base de datos, DEBES migrar sus contraseñas:

```bash
python scripts/migrar_passwords.py
```

Este script:
- ✅ Crea backup automático
- ✅ Convierte contraseñas a hash bcrypt
- ✅ Mantiene compatibilidad temporal
- ✅ Muestra resumen detallado

### 5. Actualizar Supabase (Opcional)

Agregar nueva columna para hashes (recomendado):

```sql
-- Ejecutar en SQL Editor de Supabase
ALTER TABLE usuarios 
ADD COLUMN IF NOT EXISTS password_hash TEXT;
```

---

## 🔐 Características de Seguridad

### 1. Hash de Contraseñas

**Antes:**
```python
if usuario.get("Contraseña") == password_input:  # ❌ Texto plano
```

**Ahora:**
```python
from app.utils.security import verify_password
if verify_password(password_input, usuario.get("password_hash")):  # ✅ Hash bcrypt
```

**Requisitos de contraseña:**
- Mínimo 8 caracteres
- Al menos 1 mayúscula
- Al menos 1 minúscula  
- Al menos 1 número

### 2. Protección CSRF

Todos los formularios POST están protegidos automáticamente contra Cross-Site Request Forgery.

**En templates:**
```html
<form method="POST">
    {{ csrf_token() }}  <!-- Auto-generado -->
    <!-- campos del formulario -->
</form>
```

### 3. Rate Limiting

Límites implementados:
- **Global:** 200 requests/día, 50/hora
- **Login:** 5 intentos/minuto
- **Password Reset:** 3 requests/hora

### 4. Validación de Inputs

```python
from app.utils.security import sanitizar_input, validar_email, validar_rut_chileno

# Sanitización automática
nombre = sanitizar_input(request.form.get('nombre'))

# Validaciones
if not validar_email(email):
    return error("Email inválido")
```

### 5. Logging Seguro

```python
from app.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Acción exitosa")
logger.error("Error crítico", exc_info=True)
```

Logs rotan automáticamente (max 10MB, 5 backups).

---

## ⚙️ Configuración por Entorno

### Desarrollo

```env
FLASK_ENV=development
SECRET_KEY=dev_secret_key_aqui
SESSION_COOKIE_SECURE=False
```

### Producción

```env
FLASK_ENV=production
SECRET_KEY=super_secret_key_generada_con_secrets
SESSION_COOKIE_SECURE=True
BASE_URL=https://tudominio.com
```

---

## 🛡️ Checklist de Seguridad para Producción

Antes de desplegar:

- [ ] SECRET_KEY única y segura (32+ caracteres)
- [ ] `FLASK_ENV=production`
- [ ] `SESSION_COOKIE_SECURE=True`
- [ ] HTTPS configurado (certificado SSL)
- [ ] `.env` en `.gitignore`
- [ ] Contraseñas migradas a hash
- [ ] Credenciales de Supabase cambiadas
- [ ] Contraseña de correo actualizada
- [ ] Backups de base de datos configurados
- [ ] Logs monitoreados
- [ ] Rate limiting ajustado según tráfico

---

## 📚 Archivos Modificados

### Nuevos Archivos
- `app/utils/security.py` - Utilidades de seguridad
- `app/utils/logger.py` - Sistema de logging
- `app/config.py` - Configuración centralizada
- `scripts/migrar_passwords.py` - Script de migración
- `.env.example` - Template de variables de entorno
- `requirements-dev.txt` - Dependencias de desarrollo
- `INSTALACION.md` - Guía completa de instalación

### Archivos Actualizados
- `app/__init__.py` - Seguridad y logging
- `app/routes/login.py` - Verificación con hash
- `app/routes/usuarios.py` - Creación con hash
- `app/requirements.txt` - Dependencias limpias
- `.gitignore` - Más completo

---

## 🐛 Problemas Comunes

### Error: "SECRET_KEY no configurada"

```bash
# Generar y agregar al .env
python -c "import secrets; print(secrets.token_hex(32))"
```

### Error: "Import bcrypt could not be resolved"

```bash
pip install bcrypt
```

### Usuarios no pueden iniciar sesión

```bash
# Migrar contraseñas
python scripts/migrar_passwords.py
```

### CSRF Token Missing

Agregar en templates:
```html
<form method="POST">
    {{ csrf_token() }}
    <!-- formulario -->
</form>
```

---

## 📞 Soporte

Para dudas o problemas:
1. Revisar logs en `app.log`
2. Ver documentación en `INSTALACION.md`
3. Abrir issue en GitHub

---

## 🎯 Próximos Pasos Recomendados

1. **Tests Automatizados**
   - Implementar pytest para testing
   - Cobertura de código >80%

2. **Documentación API**
   - Generar especificación OpenAPI
   - Documentar todos los endpoints

3. **Monitoreo**
   - Configurar Sentry para errores
   - Métricas de rendimiento

4. **CI/CD**
   - GitHub Actions para tests
   - Deploy automático

---

**Última actualización:** $(date)
**Versión:** 2.0.0 (Secure Edition)
