# Guía de Mantenimiento de Alertas

## 📋 Estado Actual de la Base de Datos

Después de la limpieza (9 de diciembre, 2025):
- **Total de alertas:** 794
- **Pendientes:** 11 (incluye 6 de peso)
- **Resueltas:** 650
- **Descartadas:** 130
- **Activas:** 3

## 🛠️ Script de Limpieza

### Ubicación
```
weigence/scripts/limpiar_alertas_duplicadas.py
```

### Comandos Disponibles

#### 1️⃣ Análisis sin cambios (modo prueba)
Muestra qué alertas duplicadas existen sin eliminar nada:
```bash
cd weigence
C:/Users/Gamer/Documents/GitHub/weigence-project/.venv/Scripts/python.exe scripts/limpiar_alertas_duplicadas.py
```

#### 2️⃣ Eliminar solo duplicados (RECOMENDADO)
Mantiene 1 alerta por cada discrepancia real, elimina copias:
```bash
cd weigence
C:/Users/Gamer/Documents/GitHub/weigence-project/.venv/Scripts/python.exe scripts/limpiar_alertas_duplicadas.py --ejecutar
```

#### 3️⃣ Eliminar TODAS las alertas de peso
Útil para empezar desde cero (se regenerarán las reales):
```bash
cd weigence
C:/Users/Gamer/Documents/GitHub/weigence-project/.venv/Scripts/python.exe scripts/limpiar_alertas_duplicadas.py --limpiar-todo --confirmar
```

#### 4️⃣ Ver estadísticas generales
```bash
cd weigence
C:/Users/Gamer/Documents/GitHub/weigence-project/.venv/Scripts/python.exe scripts/limpiar_alertas_duplicadas.py --stats
```

## ❓ Preguntas Frecuentes

### ¿Qué hace el script?

**Opción 2 (--ejecutar):**
- ✅ Identifica alertas duplicadas (mismo título + mismo estante)
- ✅ Mantiene la más reciente de cada grupo
- ✅ Marca las duplicadas como "descartada" (NO las elimina permanentemente)
- ✅ Preserva el historial para auditoría

**Opción 3 (--limpiar-todo):**
- 🗑️ Marca TODAS las alertas de peso como "descartada"
- 🔄 Las alertas se regenerarán automáticamente si persiste la discrepancia
- ⚡ Con el fix implementado, solo se creará 1 alerta por discrepancia

### ¿Si borro todas las alertas, se generan nuevamente?

**Sí, PERO solo si hay un problema real:**

1. **Si hay discrepancia de peso real** → Se creará 1 alerta (no duplicada) ✅
2. **Si NO hay discrepancia** → No se crea ninguna alerta ✅
3. **Si corriges el peso del estante** → La alerta se marca como "resuelta" ✅

### ¿Cómo evitar que se vuelvan a duplicar?

El **fix ya está implementado** en estos archivos:
- ✅ `app/static/js/inventario.js` - Previene llamadas concurrentes (frontend)
- ✅ `app/routes/alertas.py` - Verifica duplicados antes de insertar (backend)

**Las alertas ya NO se duplicarán** gracias a la doble capa de protección.

### ¿Qué pasa si tengo demasiadas alertas antiguas?

Puedes limpiar alertas antiguas resueltas/descartadas con SQL directo:

```sql
-- Ver alertas antiguas (más de 90 días)
SELECT estado, COUNT(*) 
FROM alertas 
WHERE fecha_creacion < NOW() - INTERVAL '90 days'
GROUP BY estado;

-- Eliminar alertas resueltas/descartadas antiguas (PERMANENTE)
DELETE FROM alertas 
WHERE estado IN ('resuelto', 'descartada') 
AND fecha_creacion < NOW() - INTERVAL '90 days';
```

## 📊 Monitoreo de Duplicados

### Query SQL para detectar duplicados
```sql
-- Detectar alertas duplicadas pendientes
SELECT 
    titulo, 
    id_estante, 
    COUNT(*) as cantidad,
    array_agg(id ORDER BY fecha_creacion DESC) as ids
FROM alertas
WHERE estado = 'pendiente' 
  AND titulo LIKE '%Discrepancia de peso%'
GROUP BY titulo, id_estante
HAVING COUNT(*) > 1;
```

### Resultado esperado después del fix
```
(0 filas) ← Sin duplicados
```

## 🔄 Flujo de Trabajo Recomendado

### Mantenimiento Semanal
```bash
# 1. Ver estadísticas
python scripts/limpiar_alertas_duplicadas.py --stats

# 2. Análisis de duplicados
python scripts/limpiar_alertas_duplicadas.py

# 3. Si hay duplicados, eliminarlos
python scripts/limpiar_alertas_duplicadas.py --ejecutar
```

### Si quieres empezar desde cero
```bash
# Limpiar todas las alertas de peso
python scripts/limpiar_alertas_duplicadas.py --limpiar-todo --confirmar

# Esperar 20 segundos (se regeneran automáticamente)
# O visitar la página de inventario para forzar regeneración
```

## 🎯 Mejores Prácticas

1. **NO eliminar alertas manualmente desde Supabase** sin usar el script
2. **Ejecutar análisis antes de limpiar** (primero sin --ejecutar)
3. **Las alertas marcadas como "descartada" NO se procesan** pero se mantienen para historial
4. **Si una alerta persiste**, significa que hay una discrepancia real de peso que debe corregirse

## 🚨 Troubleshooting

### Si ves que se siguen duplicando alertas:

1. **Verificar que el fix esté aplicado:**
   ```bash
   # Buscar el flag isLoadingAlertas en inventario.js
   grep -n "isLoadingAlertas" app/static/js/inventario.js
   
   # Buscar la verificación de duplicados en alertas.py
   grep -n "Alerta duplicada detectada" app/routes/alertas.py
   ```

2. **Verificar el log de la aplicación:**
   Deberías ver mensajes como:
   ```
   ⚠️ Alerta duplicada detectada y omitida: Discrepancia de peso en E3
   ✅ Insertadas 3 alertas de peso de estantes
   ```

3. **Limpiar caché del navegador:**
   ```
   Ctrl + Shift + Delete → Limpiar caché
   ```

### Si no aparecen alertas después de limpiar todo:

1. **Forzar regeneración:**
   - Visitar la página de inventario
   - O llamar manualmente al endpoint:
     ```bash
     curl http://localhost:5000/api/generar_alertas_basicas
     ```

2. **Verificar que haya discrepancias reales:**
   ```sql
   SELECT 
       id_estante,
       nombre,
       peso_actual,
       peso_objetivo,
       ABS(peso_actual - peso_objetivo) as diferencia
   FROM estantes
   WHERE ABS(peso_actual - peso_objetivo) > GREATEST(1, peso_objetivo * 0.02)
     AND peso_objetivo > 0;
   ```

## 📝 Historial de Cambios

- **2025-12-09:** 
  - ✅ Fix implementado para prevenir duplicados
  - ✅ Script de limpieza creado
  - ✅ Limpieza inicial: 6 duplicados eliminados
  - ✅ Estado final: 6 alertas de peso únicas, 0 duplicados

## 🎓 Para Entender el Código

### Cómo funciona la detección de duplicados:

```python
# En generar_alertas_peso_estantes()
for alerta in nuevas:
    titulo = alerta["titulo"]
    id_estante = alerta["id_estante"]
    
    # Buscar alertas pendientes con mismo título+estante en últimos 30 seg
    hace_30_seg = (datetime.now() - timedelta(seconds=30)).isoformat()
    duplicadas = supabase.table("alertas")\
        .select("id")\
        .eq("titulo", titulo)\
        .eq("id_estante", id_estante)\
        .eq("estado", "pendiente")\
        .gte("fecha_creacion", hace_30_seg)\
        .execute().data or []
    
    if not duplicadas:
        alertas_a_insertar.append(alerta)  # ✅ Insertar
    else:
        print(f"⚠️ Alerta duplicada detectada y omitida")  # 🛑 Omitir
```

Esta verificación ocurre **justo antes de insertar** en la base de datos, atrapando cualquier intento de duplicación que pase la primera capa de defensa del frontend.
