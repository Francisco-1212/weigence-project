# Archivos y Carpetas a Eliminar - Limpieza Proyecto Weigence

## 📋 Instrucciones
Elimina los siguientes archivos y carpetas para limpiar el proyecto de archivos innecesarios, duplicados y de desarrollo.

---

## ❌ Archivos de Documentación/Tesis (Raíz del Proyecto)
```
BORRADOR_TESIS.md
CONTEXTO_TESIS.md
DIAGRAMA_ARQUITECTURA.md
DIAGRAMA_PUNTO_9.md
```

## ❌ Archivos de Requirements Duplicados (Raíz del Proyecto)
```
requirements-rpb.txt
```
**Mantener:** `requirements.txt`

---

## ❌ Archivos de Debug y Pruebas (Carpeta weigence/)
```
weigence/_tmp_fix_modal.py
weigence/backup_passwords_20251117_153236.json
weigence/CHAT_REACCIONES_IMPLEMENTACION.md
weigence/check_schema.py
weigence/debug_auditoria_access.py
weigence/debug_comparar_usuarios.py
weigence/debug_roles.py
weigence/debug_sesion.py
weigence/debug_usuarios_conectados.py
weigence/debug_usuarios_supabase.py
weigence/EJEMPLO_WEBSOCKET_FRONTEND.js
weigence/INICIO.txt
weigence/LISTA_COMPLETA_ARCHIVOS.txt
weigence/RESUMEN_VISUAL_IMPLEMENTACION.txt
weigence/temp.txt
weigence/verificar_campos_supabase.py
weigence/verificar_roles.py
```

## ❌ Archivos de Testing HTML (Carpeta weigence/)
```
weigence/test_api.html
weigence/test_chat_flotante.html
weigence/test_chat.html
weigence/test_chat.py
weigence/test_email.py
weigence/test_estantes_peso.py
weigence/test_header_messages.py
weigence/test_ml_final.py
weigence/test_numero_celular.py
weigence/test_perfil_validation.py
weigence/test_products_weight.py
weigence/test_shelves.py
```

## ❌ Scripts de Diagnóstico Creados Recientemente (Carpeta weigence/)
```
weigence/diagnosticar_errores.py
weigence/eliminar_errores_prueba.py
weigence/generar_error_prueba.py
weigence/limpiar_todos_errores.py
weigence/test_audit_api.py
weigence/test_db_direct.py
weigence/verificar_errores_db.py
```

## ❌ Requirements Duplicados (Carpeta weigence/app/)
```
weigence/app/requirements.txt
```
**Mantener:** Solo el `requirements.txt` de la raíz del proyecto

---

## ❌ Carpetas Completas a Eliminar

### Carpeta docs/ (Documentación de Desarrollo)
```
weigence/docs/
```
Esta carpeta contiene más de 100 archivos markdown de documentación de desarrollo que no son necesarios para producción.

### Carpeta migrations/ (Si no usas migraciones)
```
weigence/migrations/
```
**Solo si no usas Alembic o Flask-Migrate**

### Carpeta data/ (Si está vacía o con datos de prueba)
```
weigence/data/
```
Verifica su contenido primero

---

## ❌ Archivos de Cache y Temporales

### Python Cache
```
weigence/**/__pycache__/
weigence/**/*.pyc
weigence/**/*.pyo
```

### Logs
```
weigence/app.log
weigence/app.log.1
weigence/app.log.2
```
(Se regenerarán automáticamente)

---

## ✅ Archivos y Carpetas ESENCIALES a MANTENER

### Raíz del Proyecto
- `requirements.txt`

### Carpeta weigence/
- `app.py` - Aplicación principal
- `.env` - Variables de entorno (IMPORTANTE)
- `package.json` - Dependencias Node (si las usas)

### Carpetas Esenciales en weigence/
- `app/` - Aplicación Flask completa
  - `__init__.py`
  - `app_config.py`
  - `chat/`
  - `config/`
  - `db/`
  - `ia/`
  - `routes/`
  - `static/`
  - `templates/`
  - `utils/`
- `api/` - APIs externas
  - `conexion_supabase.py`
  - `auditoria.py`
  - `historial-mov.py`
  - `recomendaciones-ai.py`
- `scripts/` - Scripts de utilidad necesarios
- `sql/` - Scripts SQL (si los usas)

---

## 🔧 Comando PowerShell para Limpiar

Puedes usar este script para eliminar archivos de forma segura:

```powershell
# Navegar a la carpeta del proyecto
cd "E:\Github\Nueva carpeta\weigence-project\weigence"

# Eliminar archivos de debug
Remove-Item -Path "_tmp_fix_modal.py", "check_schema.py", "debug_*.py", "verificar_*.py" -ErrorAction SilentlyContinue

# Eliminar archivos de test
Remove-Item -Path "test_*.py", "test_*.html" -ErrorAction SilentlyContinue

# Eliminar documentación de desarrollo
Remove-Item -Path "*.txt", "*.md" -Exclude "README.md" -ErrorAction SilentlyContinue

# Eliminar scripts de diagnóstico
Remove-Item -Path "diagnosticar_errores.py", "eliminar_errores_prueba.py", "generar_error_prueba.py", "limpiar_todos_errores.py" -ErrorAction SilentlyContinue

# Eliminar backups
Remove-Item -Path "backup_*.json" -ErrorAction SilentlyContinue

# Eliminar carpeta docs completa
Remove-Item -Path "docs" -Recurse -Force -ErrorAction SilentlyContinue

# Eliminar cache Python
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Recurse -File -Filter "*.pyc" | Remove-Item -Force

# Eliminar logs
Remove-Item -Path "app.log*" -ErrorAction SilentlyContinue
```

---

## ⚠️ IMPORTANTE - Antes de Eliminar

1. **Haz un backup completo del proyecto**
2. **Verifica que tienes `.env` guardado en lugar seguro**
3. **Confirma que `requirements.txt` está completo**
4. **Revisa `scripts/` y `sql/` por si hay algo crítico**

---

## 📊 Resumen de Limpieza

| Categoría | Cantidad Aproximada |
|-----------|---------------------|
| Archivos de debug/test | ~30 archivos |
| Documentación markdown | ~100+ archivos |
| Cache Python | Variable |
| Total estimado | **130-150 archivos** |

**Espacio a liberar:** Aproximadamente 50-100 MB

---

## ✅ Verificación Post-Limpieza

Después de eliminar, verifica que el proyecto funciona:

```powershell
# Activar entorno virtual
venv\Scripts\activate

# Instalar dependencias (por si acaso)
pip install -r requirements.txt

# Ejecutar aplicación
python app.py
```

Si todo funciona correctamente, la limpieza fue exitosa ✨
