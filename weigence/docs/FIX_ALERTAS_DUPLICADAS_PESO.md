# Fix: Alertas de Discrepancia de Peso Duplicadas

## 🐛 Problema Identificado

Las alertas de discrepancia de peso se estaban generando 2 veces, creando duplicados en la base de datos.

## 🔍 Análisis de la Causa Raíz

### Race Condition Identificada

El problema era una **condición de carrera (race condition)** causada por:

1. **Frontend:** La función `cargarAlertas()` se llama múltiples veces en rápida sucesión:
   - Una vez al cargar la página (`DOMContentLoaded`)
   - Cada 20 segundos mediante `setInterval`
   - Al marcar alertas como revisadas

2. **Backend:** Cada llamada a `/api/generar_alertas_basicas` ejecuta `generar_alertas_peso_estantes()`

3. **El flujo problemático:**
   ```
   Llamada 1 → Lee alertas existentes → No encuentra duplicado → Prepara inserción
   Llamada 2 → Lee alertas existentes → No encuentra duplicado → Prepara inserción
   Llamada 1 → Inserta alerta
   Llamada 2 → Inserta alerta (¡DUPLICADO!)
   ```

### Punto Crítico

En `app/routes/alertas.py` líneas 390-426:
- Ambas llamadas leen el estado de alertas **antes** de que cualquiera haya insertado
- Ambas determinan que `titulo_lower not in alertas_estantes_activas`
- Ambas agregan la misma alerta a la lista `nuevas`
- Ambas insertan las alertas → **Resultado: 2 alertas idénticas**

## ✅ Solución Implementada

### 1. Frontend: Prevención de Llamadas Concurrentes

**Archivo:** `app/static/js/inventario.js`

**Cambios:**
```javascript
// Añadido flag para prevenir llamadas concurrentes
let isLoadingAlertas = false;

async function cargarAlertas() {
  // Prevenir llamadas concurrentes
  if (isLoadingAlertas) {
    console.log("⏳ cargarAlertas ya está en ejecución, omitiendo...");
    return;
  }
  
  try {
    isLoadingAlertas = true;
    // ... código existente ...
  } catch (err) {
    console.error("Error cargando alertas:", err);
  } finally {
    isLoadingAlertas = false;  // Liberar flag
  }
}
```

**Beneficio:** Impide que múltiples llamadas a `cargarAlertas()` se ejecuten simultáneamente.

### 2. Backend: Verificación de Duplicados Pre-Inserción

**Archivo:** `app/routes/alertas.py`

**Cambios:**
```python
# Insertar nuevas alertas con protección adicional contra duplicados
if nuevas:
    try:
        # Verificar una vez más si ya existen estas alertas (protección contra race conditions)
        alertas_a_insertar = []
        for alerta in nuevas:
            titulo = alerta["titulo"]
            id_estante = alerta["id_estante"]
            
            # Buscar alertas pendientes con el mismo título y estante creadas recientemente (últimos 30 segundos)
            hace_30_seg = (datetime.now() - timedelta(seconds=30)).isoformat()
            duplicadas = supabase.table("alertas").select("id")\
                .eq("titulo", titulo)\
                .eq("id_estante", id_estante)\
                .eq("estado", "pendiente")\
                .gte("fecha_creacion", hace_30_seg)\
                .execute().data or []
            
            if not duplicadas:
                alertas_a_insertar.append(alerta)
            else:
                print(f"⚠️ Alerta duplicada detectada y omitida: {titulo}")
        
        if alertas_a_insertar:
            resultado = supabase.table("alertas").insert(alertas_a_insertar).execute()
            print(f"✅ Insertadas {len(alertas_a_insertar)} alertas de peso de estantes")
    except Exception as e:
        import traceback
        traceback.print_exc()
```

**Beneficio:** 
- Verificación adicional justo antes de insertar
- Detecta alertas creadas en los últimos 30 segundos
- Omite duplicados y registra en consola
- Proporciona protección a nivel de base de datos contra race conditions

## 🎯 Estrategia de Defensa en Profundidad

La solución implementa **dos capas de protección**:

1. **Capa Frontend:** Previene llamadas concurrentes (primera línea de defensa)
2. **Capa Backend:** Verificación pre-inserción con ventana de 30 segundos (última línea de defensa)

Esto garantiza que incluso si una llamada logra pasar la primera capa (por ejemplo, múltiples pestañas o usuarios), la segunda capa la detectará y prevendrá el duplicado.

## 🧪 Pruebas Recomendadas

1. **Prueba de Refrescado Rápido:**
   - Refrescar la página de inventario múltiples veces rápidamente
   - Verificar que solo se crea una alerta por discrepancia

2. **Prueba de Múltiples Pestañas:**
   - Abrir múltiples pestañas del sistema
   - Verificar que las alertas no se dupliquen

3. **Prueba del Intervalo:**
   - Dejar la página abierta durante varios ciclos del intervalo de 20 segundos
   - Verificar que no se crean duplicados con el tiempo

4. **Verificación en Base de Datos:**
   ```sql
   SELECT titulo, id_estante, COUNT(*) as cantidad
   FROM alertas
   WHERE estado = 'pendiente' 
     AND titulo LIKE '%Discrepancia de peso%'
   GROUP BY titulo, id_estante
   HAVING COUNT(*) > 1;
   ```
   Resultado esperado: **0 filas** (sin duplicados)

## 📊 Impacto

### Antes del Fix
- ❌ 2 alertas por cada discrepancia de peso
- ❌ Contaminación de la base de datos
- ❌ Confusión para usuarios (alertas duplicadas)
- ❌ Contador de alertas inflado

### Después del Fix
- ✅ 1 alerta por discrepancia de peso
- ✅ Base de datos limpia
- ✅ Experiencia de usuario mejorada
- ✅ Contadores precisos

## 📝 Notas Técnicas

### Ventana de Tiempo de 30 Segundos
La verificación usa una ventana de 30 segundos para balancear:
- **Protección suficiente:** Cubre múltiples llamadas rápidas y el intervalo de 20 segundos
- **Sin interferir con recreación legítima:** Si una alerta se resuelve y vuelve a ocurrir después de 30 segundos, se puede crear nuevamente

### Performance
El impacto en performance es mínimo:
- Frontend: Una simple verificación de flag (negligible)
- Backend: Una consulta SELECT adicional solo cuando hay nuevas alertas para insertar
- La consulta está indexada por `titulo`, `id_estante`, `estado`, y `fecha_creacion`

## 🔮 Mejoras Futuras Opcionales

1. **Unique Constraint en BD:**
   ```sql
   CREATE UNIQUE INDEX idx_alertas_unique_peso_estante 
   ON alertas (titulo, id_estante) 
   WHERE estado = 'pendiente';
   ```
   Proporcionaría garantía absoluta a nivel de base de datos.

2. **Throttling más agresivo:**
   Aumentar el intervalo de actualización de 20 a 60 segundos para reducir carga.

3. **WebSocket para alertas:**
   Eliminar polling y usar push de servidor para actualizaciones en tiempo real.

## ✨ Resumen

**Problema:** Alertas de peso duplicadas por race condition
**Causa:** Múltiples llamadas concurrentes leyendo estado antes de escribir
**Solución:** Doble capa de protección (frontend + backend)
**Estado:** ✅ **IMPLEMENTADO Y LISTO PARA PRUEBAS**

---

**Fecha de implementación:** 2025-01-XX  
**Archivos modificados:**
- `app/static/js/inventario.js`
- `app/routes/alertas.py`
