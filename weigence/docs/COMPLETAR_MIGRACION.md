# 🔧 COMPLETAR MIGRACIÓN - PASOS FINALES

## ⚠️ FALTA 1 PASO CRÍTICO

La migración falló porque **falta la columna `password_hash`** en Supabase.

---

## 🎯 SOLUCIÓN RÁPIDA (5 minutos)

### Paso 1: Abrir Supabase SQL Editor

1. Ve a: https://supabase.com/dashboard
2. Selecciona tu proyecto
3. Click en "SQL Editor" (panel izquierdo)
4. Click en "New query"

### Paso 2: Ejecutar SQL

Copia y pega este SQL:

```sql
-- Agregar columna password_hash
ALTER TABLE usuarios 
ADD COLUMN IF NOT EXISTS password_hash TEXT;

-- Crear índice para performance
CREATE INDEX IF NOT EXISTS idx_usuarios_password_hash 
ON usuarios(password_hash);
```

### Paso 3: Click en "Run" (▶️)

Deberías ver: `Success. No rows returned`

### Paso 4: Verificar (Opcional)

```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'usuarios' 
AND column_name = 'password_hash';
```

Debe devolver 1 fila con:
- `column_name`: password_hash
- `data_type`: text

---

## 🔄 Paso 5: Ejecutar Migración Nuevamente

Ahora SÍ ejecuta:

```bash
python scripts/migrar_passwords.py
```

Cuando te pregunte `¿Deseas continuar?`, escribe: **SI**

---

## ✅ RESULTADO ESPERADO

```
============================================================
RESUMEN DE MIGRACIÓN
============================================================
Total usuarios: 11
✅ Migrados: 11
⏭️  Ya migrados: 0
❌ Errores: 0
============================================================

✅ Migración completada exitosamente
```

---

## 🎉 DESPUÉS DE MIGRAR

1. **Probar login:**
   ```bash
   python app.py
   # Abrir: http://localhost:5000
   ```

2. **Verificar backup:**
   - Se creó: `backup_passwords_20251117_153236.json`
   - NO elimines este archivo por seguridad

---

## 📋 ARCHIVO SQL COMPLETO

Si prefieres usar el archivo completo:

**Ubicación:** `migrations/add_password_hash_column.sql`

Contiene:
- ✅ Crear columna
- ✅ Crear índice
- ✅ Comentarios
- ✅ Verificación
- ✅ SQL opcional para después

---

## 🆘 SI HAY PROBLEMAS

### Error: "permission denied"
- Asegúrate de estar logueado en Supabase
- Usa una cuenta con permisos de admin

### Error: "column already exists"
- ¡Perfecto! La columna ya existe
- Salta al Paso 5 directamente

### Error: "relation usuarios does not exist"
- Verifica el nombre de la tabla
- Puede ser `public.usuarios`

---

## 📞 SIGUIENTE PASO

**AHORA:**
1. Abre Supabase
2. Ejecuta el SQL
3. Vuelve y ejecuta: `python scripts/migrar_passwords.py`

**¿Listo?** Avísame cuando termines y revisamos el resultado.
