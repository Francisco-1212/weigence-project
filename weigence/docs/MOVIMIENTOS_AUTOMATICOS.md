# Sistema de Movimientos Automáticos desde Sensores de Peso

## 📋 Descripción General

Este sistema registra automáticamente movimientos de inventario basándose en las lecturas de peso provenientes de sensores instalados en los estantes. Cada variación de peso detectada genera un "movimiento gris" (movimiento automático) que se almacena en la base de datos.

---

## 🏗️ Arquitectura

### Flujo de Datos

```
┌─────────────────┐
│  Sensor de Peso │
│   (Hardware)    │
└────────┬────────┘
         │ Lectura cada X segundos
         ↓
┌─────────────────────┐
│ Tabla lecturas_peso │ ← Almacena todas las lecturas
│   (Supabase)        │
└─────────┬───────────┘
          │ Trigger/Webhook
          ↓
┌──────────────────────────┐
│ /api/lecturas_peso/      │
│      procesar            │ ← Procesa la lectura y calcula diferencias
│  (lecturas_peso.py)      │
└──────────┬───────────────┘
           │ Si hay variación de peso
           ↓
┌─────────────────────────────┐
│ Tabla movimientos_inventario│ ← Crea movimiento automático
│      (Supabase)             │
└──────────┬──────────────────┘
           │
           ↓
┌──────────────────────┐
│  Frontend Timeline   │ ← Muestra con estilo gris
│  (movimientos.html)  │
└──────────────────────┘
```

---

## 🗄️ Estructura de Datos

### Tabla: `lecturas_peso`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id_lectura` | SERIAL | ID único de la lectura |
| `id_estante` | INTEGER | ID del estante donde se detectó el peso |
| `peso_leido` | DECIMAL(10,2) | Peso total detectado en kg |
| `timestamp` | TIMESTAMP | Momento de la lectura |
| `es_anomalia` | BOOLEAN | Indica si es una lectura anómala |
| `diferencia_anterior` | DECIMAL(10,2) | Diferencia con la lectura anterior |

### Tabla: `movimientos_inventario` (Movimientos Automáticos)

| Campo | Tipo | Valor para Automáticos |
|-------|------|------------------------|
| `tipo_evento` | VARCHAR | `"Automático"` |
| `idproducto` | INTEGER | ID del producto (puede ser NULL si no se puede determinar) |
| `id_estante` | INTEGER | ID del estante donde ocurrió |
| `cantidad` | INTEGER | Unidades calculadas (peso_total / peso_por_unidad) |
| `peso_total` | DECIMAL | Peso total de la variación |
| `peso_por_unidad` | DECIMAL | Peso unitario del producto |
| `rut_usuario` | VARCHAR | `"sistema"` para movimientos automáticos |
| `observacion` | TEXT | Descripción automática con detalles |
| `timestamp` | TIMESTAMP | Momento del movimiento |

---

## 🔧 Implementación Backend

### Archivo: `app/routes/lecturas_peso.py`

**Endpoint principal: `/api/lecturas_peso/procesar`**

#### Funcionalidad:

1. **Recibe datos de lectura del sensor**
   ```json
   {
     "id_lectura": 123,
     "id_estante": 6,
     "peso_leido": 156.0,
     "diferencia_anterior": 22.0,
     "timestamp": "2025-01-15T14:30:00",
     "es_anomalia": false
   }
   ```

2. **Valida los datos recibidos**
   - Verifica que `id_estante` y `peso_leido` estén presentes
   - Valida que `diferencia_anterior` indique un cambio significativo

3. **Consulta productos en el estante**
   ```sql
   SELECT * FROM productos 
   WHERE id_estante = ? 
   AND estado = 'activo'
   ```

4. **Calcula cantidad de unidades**
   ```python
   cantidad_unidades = abs(diferencia_peso) / peso_por_unidad
   ```

5. **Crea movimiento automático**
   ```python
   {
     "tipo_evento": "Automático",
     "idproducto": producto_id,
     "id_estante": estante_id,
     "cantidad": cantidad_calculada,
     "peso_total": diferencia_peso,
     "rut_usuario": "sistema",
     "observacion": "Movimiento detectado automáticamente por sensor de peso..."
   }
   ```

#### Respuestas del Endpoint:

**✅ Éxito (200)**
```json
{
  "success": true,
  "message": "Movimiento automático registrado",
  "movimiento_id": 456,
  "tipo_movimiento": "Automático",
  "cantidad_unidades": 2,
  "peso_total": 22.0,
  "producto": "Producto X",
  "estante": "E6"
}
```

**⚠️ Sin cambios (200)**
```json
{
  "success": true,
  "message": "Sin cambios significativos",
  "diferencia": 0.5
}
```

**❌ Error (400/500)**
```json
{
  "success": false,
  "error": "Descripción del error"
}
```

---

## 🎨 Implementación Frontend

### Archivo: `app/static/js/movimiento_inventario.js`

#### Características de Visualización:

**Movimientos Automáticos se muestran con:**

1. **Estilo gris diferenciado**
   ```javascript
   const esAutomatico = m.tipo_evento === "Automático";
   const color = esAutomatico ? "gray" : /* otros colores */;
   ```

2. **Badge de "Detección automática"**
   ```html
   <span class="material-symbols-outlined text-xs text-gray-500">sensors</span>
   <span class="text-[9px] text-gray-500">DETECCIÓN AUTOMÁTICA</span>
   ```

3. **Opacidad reducida**
   ```javascript
   class="${esAutomatico ? 'opacity-75' : ''}"
   ```

4. **Icono de sensor**
   ```html
   <span class="material-symbols-outlined">sensors</span>
   ```

5. **Colores grises en lugar de verde/rojo**
   ```css
   bg-gray-50 dark:bg-gray-800/50
   border-gray-400 dark:border-gray-600
   text-gray-600 dark:text-gray-400
   ```

#### Ejemplo Visual:

```
┌────────────────────────────────────────────────┐
│ 🔘 [SENSORS] DETECCIÓN AUTOMÁTICA              │
│                                                │
│    📦 Detección automática                     │
│    156.0 kg | 14:30                            │
│    E6 • Sistema                                │
└────────────────────────────────────────────────┘
   ↑ Tarjeta con fondo gris y opacidad 75%
```

---

## 🔄 Integración con la Aplicación

### Registro del Blueprint

En `app/__init__.py`:

```python
# Registrar blueprint de lecturas de peso (sensores automáticos)
from app.routes.lecturas_peso import bp as lecturas_bp
app.register_blueprint(lecturas_bp)
```

### Modificaciones en Movimientos

En `app/routes/movimientos.py`:

```python
# Detectar movimientos automáticos
es_automatico = m.get("tipo_evento") == "Automático"

mov = {
    # ... otros campos ...
    "usuario_nombre": "Sistema" if es_automatico else usuarios_data.get("nombre"),
    "rut_usuario": "sistema" if es_automatico else m.get("rut_usuario"),
    "es_automatico": es_automatico
}
```

---

## 🧪 Testing

### Script: `test_movimientos_automaticos.py`

**Uso:**

```bash
python test_movimientos_automaticos.py
```

**Funciones:**

1. `test_procesar_lectura_peso()` - Envía lectura simulada al endpoint
2. `test_obtener_movimientos_automaticos()` - Verifica que se listen correctamente

**Ejemplo de salida:**

```
🚀 Iniciando pruebas del sistema de movimientos automáticos

============================================================
TEST: Procesamiento de lectura de peso automática
============================================================

📊 Datos de lectura:
{
  "id_lectura": 999,
  "id_estante": 6,
  "peso_leido": 156.0,
  "diferencia_anterior": 22.0,
  ...
}

✅ Movimiento automático creado exitosamente!
ID Movimiento: 789
Tipo: Automático
Cantidad detectada: 2 unidades
Peso total: 22.0 kg
```

---

## 📊 Casos de Uso

### 1. Cliente retira productos del estante

```
Sensor detecta: -22.0 kg
Sistema calcula: 22 / 11 = 2 unidades retiradas
Movimiento creado: Tipo "Automático", Cantidad -2
```

### 2. Cliente añade productos al estante

```
Sensor detecta: +33.0 kg
Sistema calcula: 33 / 11 = 3 unidades añadidas
Movimiento creado: Tipo "Automático", Cantidad +3
```

### 3. Cambio mínimo (ruido del sensor)

```
Sensor detecta: +0.3 kg
Sistema ignora: Diferencia < umbral mínimo
No se crea movimiento
```

### 4. Anomalía detectada

```
Sensor detecta: es_anomalia = true
Sistema registra: Con observación especial
Movimiento marcado como anómalo
```

---

## ⚙️ Configuración

### Variables de Entorno

```env
# Umbral mínimo de peso para registrar movimiento (kg)
PESO_MINIMO_MOVIMIENTO=1.0

# Tiempo entre lecturas del sensor (segundos)
SENSOR_INTERVALO_LECTURA=5

# Activar logs de debug para movimientos automáticos
DEBUG_MOVIMIENTOS_AUTO=True
```

### Configuración en Base de Datos

**Trigger para procesamiento automático:**

```sql
CREATE OR REPLACE FUNCTION procesar_lectura_peso()
RETURNS TRIGGER AS $$
BEGIN
    -- Llamar al endpoint de la aplicación
    PERFORM net.http_post(
        url := 'http://tu-app.com/api/lecturas_peso/procesar',
        body := jsonb_build_object(
            'id_lectura', NEW.id_lectura,
            'id_estante', NEW.id_estante,
            'peso_leido', NEW.peso_leido,
            'diferencia_anterior', NEW.diferencia_anterior
        )
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_nueva_lectura
    AFTER INSERT ON lecturas_peso
    FOR EACH ROW
    EXECUTE FUNCTION procesar_lectura_peso();
```

---

## 🐛 Troubleshooting

### Problema: Los movimientos automáticos no se crean

**Verificar:**
1. ¿El blueprint está registrado? → Revisar `app/__init__.py`
2. ¿La tabla `lecturas_peso` existe? → `SELECT * FROM lecturas_peso LIMIT 1`
3. ¿El endpoint responde? → `curl http://localhost:5000/api/lecturas_peso/procesar`
4. ¿Hay productos activos en el estante? → `SELECT * FROM productos WHERE id_estante = X`

### Problema: Los movimientos no se muestran con estilo gris

**Verificar:**
1. ¿El campo `tipo_evento` es "Automático"? → Revisar en base de datos
2. ¿El JavaScript detecta correctamente? → Console log en navegador
3. ¿TailwindCSS carga las clases grises? → Inspeccionar elemento

### Problema: Cálculo de unidades incorrecto

**Verificar:**
1. ¿El producto tiene `peso_por_unidad` correcto?
2. ¿La diferencia de peso es la esperada?
3. ¿Hay múltiples productos en el mismo estante? → Puede causar ambigüedad

---

## 📝 Notas Importantes

1. **Múltiples productos en un estante:** El sistema actualmente asocia la variación al primer producto activo encontrado. Para mayor precisión, considera añadir lógica de identificación por zona o RFID.

2. **Umbral de detección:** Ajusta `PESO_MINIMO_MOVIMIENTO` según la precisión de tus sensores para evitar falsos positivos.

3. **Rendimiento:** Para alta frecuencia de lecturas, considera implementar procesamiento en batch o cola de mensajes (e.g., Celery, RabbitMQ).

4. **Seguridad:** El endpoint `/api/lecturas_peso/procesar` debe estar protegido con autenticación (API key, token) en producción.

5. **Auditoría:** Todos los movimientos automáticos quedan registrados con `rut_usuario = "sistema"` para fácil identificación en auditorías.

---

## 🚀 Próximas Mejoras

- [ ] Sistema de notificaciones push cuando se detecta movimiento automático
- [ ] Dashboard en tiempo real con gráficas de peso por estante
- [ ] Machine Learning para detectar patrones anómalos
- [ ] Integración con sistema de alertas para desabastecimiento
- [ ] API webhook para notificar a sistemas externos
- [ ] Configuración de umbrales personalizados por estante

---

## 📚 Referencias

- Documentación de la API: `/docs/API_REFERENCE.md`
- Arquitectura del chat: `/docs/ARQUITECTURA_CHAT.md`
- Guía de desarrollo: `/docs/ENV_QUICK_START.md`

---

**Última actualización:** 2025-01-15
**Versión:** 1.0.0
**Autor:** Equipo Weigence
