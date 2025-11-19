# 🚀 QUICK START: Sistema ML Avanzado

## ✅ Verificación Rápida (30 segundos)

```bash
# 1. Test backend
python -c "from app.ia.ia_service import generar_recomendacion; r = generar_recomendacion('auditoria'); print('✅ ML cards:', len(r['ml_insights_cards']))"

# 2. Ver mensajes completos
python test_ml_final.py

# 3. Iniciar servidor
python app.py

# 4. Abrir navegador
http://127.0.0.1:5000/auditoria
```

## 🎯 Qué Esperar

### Tarjeta IA en Auditoría
- **Ubicación**: Parte superior de `/auditoria`
- **Navegación**: Botones ← / → (o flechas de teclado)
- **Total hallazgos**: 6 módulos diferentes
- **Contador**: "1 / 6" en la esquina

### Mensajes Específicos Generados

| Módulo | Ejemplo Real |
|--------|-------------|
| 🏆 Dashboard | "Ketoprofeno 100mg" lidera ventas (6 unidades en 48h) |
| 📦 Inventario | 2 productos SIN STOCK: Crema Hidratante, Omeprazol |
| 🔍 Movimientos | 0.2 movimientos/hora. Actividad baja |
| 💰 Ventas | $10772 vs $66290 (caída del 84%) |
| 🚨 Alertas | Sistema bajo control (0 críticas activas) |
| 🕵️ Auditoría | 139 eventos, 2 usuarios activos (normal) |

## 📊 Severidad Visual

```
🟢 LOW      → Barra verde 25%
🟡 MEDIUM   → Barra naranja 50%
🟠 HIGH     → Barra naranja oscuro 75%
🔴 CRITICAL → Barra roja 100%
```

## 🔧 Troubleshooting

### No aparece tarjeta IA
```bash
# Verificar que ML detecte anomalía
python -c "from app.ia.ia_ml_anomalies import detect_anomalies; from app.ia.ia_service import _obtener_snapshot; s = _obtener_snapshot(); r = detect_anomalies(s); print('ML detected:', r['is_anomaly'])"
```

### Mensajes genéricos en vez de específicos
```bash
# Verificar datos en Supabase
python -c "from api.conexion_supabase import supabase; dv = supabase.table('detalle_ventas').select('*').limit(1).execute(); print('Data OK:', len(dv.data) > 0)"
```

### Errores en consola
```bash
# Ver logs detallados
python app.py 2>&1 | grep -i "error\|traceback"
```

## 🗂️ Archivos Modificados

```
✅ Creados:
   app/ia/ia_ml_insights_advanced.py

✅ Modificados:
   app/ia/ia_ml_anomalies.py
   app/templates/pagina/auditoria.html
   app/static/js/recomendaciones.js
   app/static/css/ia-recommendation.css
```

## 📝 Notas Importantes

1. **Datos reales**: Sistema lee de Supabase en tiempo real
2. **Sin caché**: Cada request genera análisis fresco
3. **Fallback**: Si falla query, muestra mensaje genérico
4. **Performance**: ~500ms de análisis ML + queries
5. **Lazy loading**: Supabase se importa solo cuando se necesita

## 🎨 Personalización

### Cambiar umbrales
Editar `app/ia/ia_ml_insights_advanced.py`:
```python
# Línea 94 - Stock bajo
elif stock <= 5:  # Cambiar de 5 a X

# Línea 311 - Actividad sospechosa
if events_per_hour > 20:  # Cambiar de 20 a X
```

### Modificar ventana de tiempo
```python
# Línea 45 - Rankings
timedelta(hours=48)  # Cambiar 48h

# Línea 193 - Ventas
timedelta(hours=24)  # Cambiar 24h
```

### Ajustar mensajes
Editar `app/ia/ia_ml_anomalies.py` líneas 413-637:
```python
findings.append({
    'titulo': f'Tu mensaje personalizado',
    'descripcion': f'Con variables {data["valor"]}',
    'plan_accion': 'Acción específica'
})
```

---

**Documentación completa**: `IMPLEMENTACION_ML_AVANZADO.md`
