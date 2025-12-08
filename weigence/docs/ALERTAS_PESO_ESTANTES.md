# Sistema de Alertas de Peso de Estantes

## Resumen

Se ha implementado un sistema automático de alertas que monitorea la diferencia entre el peso actual y el peso objetivo de cada estante, generando notificaciones cuando existe una discrepancia significativa.

## Funcionalidad Implementada

### 1. **Generación Automática de Alertas** (`generar_alertas_peso_estantes()`)

Esta función se ejecuta automáticamente y realiza las siguientes acciones:

#### Criterios de Alerta

- **Umbral de Diferencia**: Se considera significativa cuando:
  - La diferencia es mayor a 5kg, O
  - La diferencia es mayor al 5% del peso objetivo
  - Se usa el valor mayor entre ambos

#### Tipos de Discrepancia

**Exceso de Peso** (peso_actual > peso_objetivo)
- **Tipo**: Naranja
- **Icono**: trending_up
- **Descripción**: Indica que el estante tiene más peso del esperado
- **Ejemplo**: "El estante tiene 12.50kg más de lo esperado. Peso actual: 87.50kg, Objetivo: 75.00kg (16.7% de diferencia)"

**Faltante de Peso** (peso_actual < peso_objetivo)
- **Tipo**: Amarilla
- **Icono**: trending_down
- **Descripción**: Indica que al estante le falta peso
- **Ejemplo**: "Al estante le faltan 8.30kg. Peso actual: 66.70kg, Objetivo: 75.00kg (11.1% de diferencia)"

### 2. **Gestión Inteligente de Alertas**

#### Creación de Alertas
- Se crea una nueva alerta cuando se detecta una discrepancia significativa
- Cada alerta incluye:
  - Título: "Discrepancia de peso en [Nombre del Estante]"
  - Descripción detallada con valores y porcentaje
  - ID del estante (`id_estante`)
  - Estado: "pendiente"
  - Campos `idproducto` e `idusuario` como `NULL`

#### Reactivación de Alertas
- Si existe una alerta resuelta previamente y la discrepancia vuelve a aparecer
- Se reactiva la alerta existente cambiando su estado a "pendiente"
- Se actualiza la descripción con los valores actuales

#### Resolución Automática
- Cuando el peso vuelve a estar dentro del rango aceptable
- Las alertas activas se marcan automáticamente como "resueltas"

### 3. **Integración con el Sistema de Alertas Existente**

#### Backend (`alertas.py`)

**Nueva Función**:
```python
def generar_alertas_peso_estantes():
    """
    Crea o actualiza alertas cuando el peso_actual de un estante 
    difiere del peso_objetivo.
    """
```

**Endpoint Actualizado**:
```python
@bp.route("/api/generar_alertas_basicas")
def generar_alertas_basicas_api():
    resultado_productos = generar_alertas_basicas()
    resultado_estantes = generar_alertas_peso_estantes()
    # Retorna éxito si al menos una función se ejecutó correctamente
```

**Ejecución Automática**:
- Se ejecuta al cargar la página de alertas
- Se puede llamar manualmente desde el endpoint API

#### Frontend

**HTML (`alertas.html`)**:
- Agregado campo `data-estante` en las filas de la tabla
- Nuevo contenedor en el modal para mostrar el estante
- Icono `shelf_position` para identificar alertas de estantes
- Visualización condicional: solo muestra el campo si existe un estante asociado

**JavaScript (`alertas.js`)**:
- Nuevas variables en `cacheDOM()`:
  - `modalEstante`: elemento para mostrar el nombre del estante
  - `modalEstanteContainer`: contenedor del campo estante
- Lógica actualizada en `abrirModal()`:
  - Muestra el estante solo si existe y no está vacío
  - Oculta el campo producto si es "Sin producto"

### 4. **Datos de la Tabla Estantes**

La función consulta la tabla `estantes` con los siguientes campos:
- `id_estante`: ID único del estante (requerido para la alerta)
- `nombre`: Nombre del estante para mostrar
- `peso_actual`: Peso actual registrado
- `peso_objetivo`: Peso esperado/objetivo

### 5. **Datos de la Tabla Alertas**

Las alertas de estantes utilizan la siguiente estructura:
```sql
{
  "id": int,
  "titulo": "Discrepancia de peso en [Nombre]",
  "descripcion": "Detalles de la diferencia...",
  "icono": "trending_up" | "trending_down",
  "tipo_color": "naranja" | "amarilla",
  "fecha_creacion": timestamp,
  "estado": "pendiente" | "resuelto",
  "idproducto": NULL,
  "idusuario": NULL,
  "id_estante": int (NOT NULL),
  "fecha_modificacion": timestamp
}
```

## Ventajas del Sistema

1. **Detección Automática**: No requiere intervención manual
2. **Resolución Inteligente**: Se resuelven automáticamente cuando el problema se corrige
3. **Información Detallada**: Incluye valores exactos y porcentajes
4. **Prevención de Duplicados**: Gestiona alertas existentes en lugar de crear duplicados
5. **Integración Completa**: Se integra perfectamente con el sistema de alertas existente
6. **Visualización Clara**: Distingue entre exceso y faltante de peso

## Casos de Uso

### Ejemplo 1: Exceso de Peso
```
Estante: E6 (T-Z)
Peso Actual: 73.00 kg
Peso Objetivo: 52.60 kg
Diferencia: 20.40 kg (38.8%)

Resultado: Alerta NARANJA con icono trending_up
```

### Ejemplo 2: Faltante de Peso
```
Estante: E3 (G-J)
Peso Actual: 600.00 kg
Peso Objetivo: 650.00 kg
Diferencia: 50.00 kg (7.7%)

Resultado: Alerta AMARILLA con icono trending_down
```

### Ejemplo 3: Dentro del Rango
```
Estante: E1 (A-C)
Peso Actual: 50.50 kg
Peso Objetivo: 50.00 kg
Diferencia: 0.50 kg (1.0%)

Resultado: No se genera alerta (diferencia < 5% y < 5kg)
```

## Monitoreo y Mantenimiento

### Logs
El sistema genera logs informativos:
```
[ALERTA] 3 nuevas alertas de peso de estantes creadas.
[ALERTA] Resuelta discrepancia de peso en E6 (T-Z)
```

### Consulta Manual
Para generar alertas manualmente:
```bash
GET /api/generar_alertas_basicas
```

### Verificación
Consultar alertas de estantes activas:
```sql
SELECT * FROM alertas 
WHERE id_estante IS NOT NULL 
AND estado = 'pendiente'
ORDER BY fecha_creacion DESC;
```

## Archivos Modificados

1. **Backend**:
   - `weigence/app/routes/alertas.py`
     - Nueva función: `generar_alertas_peso_estantes()`
     - Endpoint actualizado: `/api/generar_alertas_basicas`
     - Ruta de alertas actualizada para generar automáticamente

2. **Frontend - HTML**:
   - `weigence/app/templates/pagina/alertas.html`
     - Agregado `data-estante` en filas de tabla
     - Nuevo campo en modal para mostrar estante

3. **Frontend - JavaScript**:
   - `weigence/app/static/js/alertas.js`
     - Nuevos elementos en `cacheDOM()`
     - Lógica actualizada en `abrirModal()`

## Configuración

### Ajustar Umbral de Alerta
Para cambiar el umbral de detección, modificar en `generar_alertas_peso_estantes()`:

```python
# Actual: 5% o 5kg
umbral_kg = max(5, peso_objetivo * 0.05)

# Ejemplo: 10% o 10kg
umbral_kg = max(10, peso_objetivo * 0.10)
```

### Cambiar Colores de Alerta
```python
# Para exceso
tipo_color = "naranja"  # Cambiar a "rojo" para mayor urgencia

# Para faltante
tipo_color = "amarilla"  # Cambiar a "amarilla" o "naranja"
```

## Futuras Mejoras

1. **Historial de Variaciones**: Registrar cambios en el tiempo
2. **Alertas por Hora**: Detectar cambios bruscos en períodos cortos
3. **Predicción**: Usar ML para predecir discrepancias antes de que ocurran
4. **Notificaciones Push**: Enviar alertas en tiempo real
5. **Dashboard Visual**: Gráficos de tendencias de peso por estante
