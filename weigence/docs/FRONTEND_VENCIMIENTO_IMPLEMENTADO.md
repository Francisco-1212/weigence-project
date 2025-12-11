# ✅ Sistema de Vencimiento - Frontend Implementado

## 📋 Resumen de Implementación

Se ha implementado completamente el sistema de fechas de elaboración y vencimiento en el frontend de la página de inventario.

---

## 🎨 Componentes Implementados

### 1. **Tabla de Inventario** (`inventario.html`)

#### Columnas Agregadas:
- **F. Elab.** (Fecha de Elaboración) - `hidden lg:table-cell`
- **F. Venc.** (Fecha de Vencimiento) - `hidden lg:table-cell`
- **Vencimiento** (Estado con badge) - `hidden xl:table-cell`

#### Badges de Estado:
```html
<!-- Vencido/Vence Hoy - Rojo -->
<span class="bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-400">
  <span class="material-symbols-outlined">dangerous</span> Vencido
</span>

<!-- Crítico (≤7 días) - Naranja -->
<span class="bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-400">
  <span class="material-symbols-outlined">warning</span> 7d
</span>

<!-- Próximo (≤30 días) - Amarillo -->
<span class="bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-400">
  <span class="material-symbols-outlined">schedule</span> 15d
</span>

<!-- Vigente (>30 días) - Verde -->
<span class="bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-400">
  <span class="material-symbols-outlined">check_circle</span> Vigente
</span>
```

#### Atributos Data para Filtrado:
```html
<tr class="product-row"
    data-vencimiento="critico"
    data-fecha-venc="2024-12-25">
```

---

### 2. **Botones de Filtro** (`inventario.html`)

Se agregaron 3 nuevos botones de filtro después de un separador visual:

```html
<!-- Separador -->
<div class="w-px h-6 bg-gray-300 dark:bg-neutral-700 hidden sm:block"></div>

<!-- Filtro Vencidos -->
<button class="filtro-venc-btn" data-vencimiento="vencido">
  <span class="material-symbols-outlined">dangerous</span>Vencidos
</button>

<!-- Filtro Críticos (≤7 días) -->
<button class="filtro-venc-btn" data-vencimiento="critico">
  <span class="material-symbols-outlined">warning</span>Críticos
</button>

<!-- Filtro Próximos (≤30 días) -->
<button class="filtro-venc-btn" data-vencimiento="proximo">
  <span class="material-symbols-outlined">schedule</span>Próximos
</button>
```

**Estilos:**
- Borde de color según el estado (rojo/naranja/amarillo)
- Texto de color matching
- Hover con fondo sutil del color correspondiente

---

### 3. **Modal de Producto** (`inventario.js`)

#### Campos Agregados en `formAdd()`:
```html
<div>
  <label>Fecha de Elaboración</label>
  <input type="date" name="fecha_elaboracion" id="fecha_elaboracion">
</div>

<div>
  <label>Fecha de Vencimiento</label>
  <input type="date" name="fecha_vencimiento" id="fecha_vencimiento">
</div>

<!-- Panel de advertencias dinámico -->
<div id="fecha_warning" class="hidden">
  <span class="material-symbols-outlined">warning</span>
  <span id="fecha_warning_text"></span>
</div>
```

#### Campos en `formEdit()`:
Igual que `formAdd()` pero con valores prellenados:
```javascript
<input type="date" name="fecha_elaboracion" value="${p.fecha_elaboracion || ''}">
<input type="date" name="fecha_vencimiento" value="${p.fecha_vencimiento || ''}">
```

---

### 4. **Sección de Detalles** (`inventario.js`)

Se agregó una nueva tarjeta "Fechas y Vencimiento":

```javascript
<div class="bg-[var(--card-bg-dark)] p-4 rounded-lg">
  <h4>Fechas y Vencimiento</h4>
  <div class="space-y-2">
    <p>Fecha Elaboración: ${p.fecha_elaboracion_formato || 'N/A'}</p>
    <p>Fecha Vencimiento: ${p.fecha_vencimiento_formato || 'N/A'}</p>
    <p>Estado: <span class="badge-vencimiento">${p.estado_vencimiento.mensaje}</span></p>
  </div>
</div>
```

---

## ⚙️ Funciones JavaScript Implementadas

### 1. **`validarFechas(fechaElab, fechaVenc)`**

Valida que:
- ✅ La fecha de elaboración no sea posterior a la de vencimiento
- ⚠️ Muestra advertencias si el producto está:
  - Vencido (días restantes < 0)
  - Vence HOY (días restantes = 0)
  - Crítico (días restantes ≤ 7)
  - Próximo a vencer (días restantes ≤ 30)

**Interfaz visual:**
```javascript
// Error (rojo) - Elaboración > Vencimiento
warning.classList.add('bg-red-50', 'text-red-500');

// Advertencia (amarillo) - Próximo a vencer
warning.classList.add('bg-yellow-50', 'text-yellow-500');
```

**Return:**
- `false` si fecha_elaboracion > fecha_vencimiento (bloquea guardado)
- `true` en otros casos (permite guardar con advertencia)

---

### 2. **`configurarValidacionFechas()`**

Se ejecuta al abrir modal de agregar/editar:
```javascript
const fechaElab = document.getElementById('fecha_elaboracion');
const fechaVenc = document.getElementById('fecha_vencimiento');

fechaElab.addEventListener('change', () => validarFechas(...));
fechaVenc.addEventListener('change', () => validarFechas(...));
```

---

### 3. **`filterByVencimiento(vencimiento)`**

Filtra productos según su estado de vencimiento:

```javascript
filterByVencimiento('vencido')  // Muestra solo vencidos + vence_hoy
filterByVencimiento('critico')  // Muestra solo críticos (≤7 días)
filterByVencimiento('proximo')  // Muestra solo próximos (≤30 días)
```

**Implementación:**
```javascript
const estadoVenc = row.getAttribute('data-vencimiento');
if (vencimiento === 'critico' && estadoVenc === 'critico') {
  row.classList.remove('hidden');
}
```

---

### 4. **Modificaciones en `saveNew()` y `saveEdit()`**

#### `saveNew()`:
```javascript
// Validar antes de enviar
if (!this.validarFechas(data.fecha_elaboracion, data.fecha_vencimiento)) {
  return; // Bloquea si elaboración > vencimiento
}

// Limpiar campos vacíos
if (!data.fecha_elaboracion) delete data.fecha_elaboracion;
if (!data.fecha_vencimiento) delete data.fecha_vencimiento;

// Enviar al servidor
fetch('/api/productos/agregar', {
  body: JSON.stringify(data) // Incluye fechas
});
```

#### `saveEdit()`:
```javascript
const fechaElab = fd.get('fecha_elaboracion');
const fechaVenc = fd.get('fecha_vencimiento');

if (!this.validarFechas(fechaElab, fechaVenc)) {
  return;
}

const updated = {
  ...this.state.current,
  fecha_elaboracion: fechaElab || null,
  fecha_vencimiento: fechaVenc || null
};
```

---

### 5. **Event Listeners en `bindEvents()`**

```javascript
// Filtros de vencimiento
const filtroVencBtns = document.querySelectorAll('.filtro-venc-btn');
filtroVencBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    const vencimiento = btn.getAttribute('data-vencimiento');
    this.filterByVencimiento(vencimiento);
  });
});
```

---

## 🎯 Umbrales y Colores

| Estado | Días Restantes | Color | Icono | Badge |
|--------|---------------|-------|-------|-------|
| **Vencido** | < 0 | 🔴 Rojo (#DC2626) | dangerous | "Vencido" |
| **Vence Hoy** | = 0 | 🔴 Rojo (#DC2626) | dangerous | "Vence Hoy" |
| **Crítico** | 0-7 días | 🟠 Naranja (#EA580C) | warning | "7d" |
| **Próximo** | 8-30 días | 🟡 Amarillo (#F59E0B) | schedule | "15d" |
| **Vigente** | > 30 días | 🟢 Verde (#10B981) | check_circle | "Vigente" |

---

## 📱 Responsive Design

### Breakpoints Tailwind:
- **F. Elab. y F. Venc.:** `hidden lg:table-cell` (≥1024px)
- **Estado Vencimiento:** `hidden xl:table-cell` (≥1280px)
- **Filtros:** Visible en todas las resoluciones con iconos responsivos

### Mobile:
```html
<!-- Separador oculto en móvil -->
<div class="hidden sm:block">...</div>

<!-- Botones con tamaño adaptativo -->
<button class="px-2.5 sm:px-3 py-1.5 text-xs sm:text-sm">
```

---

## 🔄 Flujo de Usuario

### Agregar Producto con Fechas:
1. Click en "Agregar Producto"
2. Llenar nombre, categoría, stock, etc.
3. **Ingresar fecha de elaboración** (opcional)
4. **Ingresar fecha de vencimiento** (opcional)
5. Sistema valida automáticamente al cambiar fechas
6. Si elaboración > vencimiento → **Error rojo** (no permite guardar)
7. Si vence en ≤30 días → **Advertencia amarilla** (permite guardar)
8. Click en "Guardar" → Envía fechas al backend

### Editar Producto:
1. Click en ícono de editar (lápiz)
2. Modal muestra fechas actuales (si existen)
3. Modificar fechas con validación en tiempo real
4. Guardar → Actualiza fechas en BD

### Filtrar por Vencimiento:
1. Click en "Vencidos" → Muestra solo productos vencidos/vencen hoy
2. Click en "Críticos" → Muestra solo productos que vencen en ≤7 días
3. Click en "Próximos" → Muestra solo productos que vencen en ≤30 días
4. Click en "Todos" → Restaura vista completa

---

## ✅ Checklist de Implementación

- [x] Columnas de fecha en tabla HTML
- [x] Columna de estado de vencimiento con badges
- [x] Botones de filtro de vencimiento
- [x] Campos de fecha en formulario de agregar
- [x] Campos de fecha en formulario de editar
- [x] Panel de advertencias dinámico
- [x] Función `validarFechas()` con validación y warnings
- [x] Función `configurarValidacionFechas()` para event listeners
- [x] Función `filterByVencimiento()` para filtrado
- [x] Integración en `saveNew()` con validación
- [x] Integración en `saveEdit()` con validación
- [x] Sección de fechas en vista de detalles
- [x] Atributos data para filtrado eficiente
- [x] Event listeners en `bindEvents()`
- [x] Responsive design con Tailwind
- [x] Iconos Material Symbols
- [x] Dark mode support

---

## 🚀 Próximos Pasos

### Pendientes del Usuario:
1. **Ejecutar migración SQL en Supabase:**
   ```sql
   -- Ver archivo: migrations/add_fechas_vencimiento.sql
   ALTER TABLE productos ADD COLUMN fecha_elaboracion DATE;
   ALTER TABLE productos ADD COLUMN fecha_vencimiento DATE;
   -- + índices y vistas
   ```

2. **Reiniciar servidor Flask:**
   ```bash
   # Ctrl+C para detener
   python app.py
   ```

3. **Probar funcionalidad:**
   - Agregar producto con fechas
   - Editar fechas de producto existente
   - Filtrar por vencidos/críticos/próximos
   - Verificar alertas automáticas
   - Exportar Excel con columnas de fecha

---

## 🐛 Testing Recomendado

### Casos de Prueba:
1. **Agregar producto sin fechas** → Debe guardar correctamente
2. **Agregar producto con fecha_elab > fecha_venc** → Error rojo, no guarda
3. **Agregar producto que vence en 5 días** → Advertencia naranja, guarda OK
4. **Agregar producto que vence en 2 meses** → Sin advertencia, guarda OK
5. **Filtrar por "Críticos"** → Solo muestra productos ≤7 días
6. **Editar fecha y cambiar de vigente a crítico** → Badge cambia de color
7. **Ver detalles de producto con fechas** → Muestra tarjeta "Fechas y Vencimiento"

---

## 📊 Integración con Backend

El frontend envía y recibe datos en este formato:

### Request (POST /api/productos/agregar):
```json
{
  "nombre": "Paracetamol",
  "categoria": "Analgésico",
  "stock": 50,
  "peso": 15.5,
  "fecha_elaboracion": "2024-01-15",
  "fecha_vencimiento": "2025-06-30"
}
```

### Response (GET /pagina/inventario):
```python
{
  "idproducto": 123,
  "nombre": "Paracetamol",
  "fecha_elaboracion": "2024-01-15",
  "fecha_vencimiento": "2025-06-30",
  "fecha_elaboracion_formato": "15/01/2024",
  "fecha_vencimiento_formato": "30/06/2025",
  "estado_vencimiento": {
    "estado": "vigente",
    "dias_restantes": 180,
    "nivel": "ok",
    "color": "verde",
    "mensaje": "Vigente"
  }
}
```

---

## 🎨 Capturas de Diseño

### Tabla con Columnas de Vencimiento:
```
| Código | Nombre    | Categoría  | Stock | F. Elab.   | F. Venc.   | Vencimiento    |
|--------|-----------|------------|-------|------------|------------|----------------|
| 001    | Med A     | Analgésico | 50    | 15/01/2024 | 30/06/2025 | ✓ Vigente      |
| 002    | Med B     | Antibiótico| 30    | 20/12/2023 | 25/12/2024 | ⚠️ 7d (Crítico)|
| 003    | Med C     | Suplemento | 10    | 05/10/2023 | 10/12/2024 | ❌ Vencido     |
```

### Filtros:
```
[Todos] [Sin Stock] [Bajo Stock] [Normal] | [🔴 Vencidos] [🟠 Críticos] [🟡 Próximos]
```

### Modal de Agregar/Editar:
```
┌─────────────────────────────────────────┐
│ Agregar Nuevo Producto                  │
├─────────────────────────────────────────┤
│ Nombre: [_______________]               │
│ Categoría: [▼____________]              │
│ Stock: [___] Peso: [___]                │
│ Fecha de Elaboración: [📅 15/01/2024]  │
│ Fecha de Vencimiento: [📅 20/12/2024]  │
│                                         │
│ ⚠️ Este producto vence en 5 días       │
│                                         │
│             [Cancelar] [Guardar]        │
└─────────────────────────────────────────┘
```

---

## 📝 Notas Técnicas

### Manejo de Fechas en JavaScript:
```javascript
// Crear fecha sin hora (00:00:00)
const ahora = new Date();
ahora.setHours(0, 0, 0, 0);

// Calcular días restantes
const diasRestantes = Math.ceil((fechaVenc - ahora) / (1000 * 60 * 60 * 24));
```

### Formato de Fecha HTML5:
```html
<!-- Input acepta formato YYYY-MM-DD -->
<input type="date" value="2024-12-25">

<!-- Backend envía formato DD/MM/YYYY para display -->
<span>25/12/2024</span>
```

### Prioridad de Colores:
En la tabla, el color del badge de vencimiento **toma prioridad** sobre el color de stock:
```javascript
// Un producto con stock bajo (amarillo) pero vencido (rojo)
// → Se muestra ROJO por vencimiento
```

---

## 📄 Archivos Modificados

1. **`app/templates/pagina/inventario.html`**
   - ✏️ Agregadas 3 columnas en `<thead>` y `<tbody>`
   - ✏️ Agregados 3 botones de filtro `.filtro-venc-btn`
   - ✏️ Agregados atributos `data-vencimiento` y `data-fecha-venc`
   - ✏️ Colspan cambiado de 9 a 12

2. **`app/static/js/inventario.js`**
   - ✏️ Agregados campos de fecha en `templates.formAdd()`
   - ✏️ Agregados campos de fecha en `templates.formEdit()`
   - ✏️ Agregada sección "Fechas y Vencimiento" en `templates.details()`
   - ✏️ Agregada función `validarFechas()`
   - ✏️ Agregada función `configurarValidacionFechas()`
   - ✏️ Agregada función `filterByVencimiento()`
   - ✏️ Modificado `showAddForm()` con validación
   - ✏️ Modificado `editProduct()` con validación
   - ✏️ Modificado `saveNew()` con validación y envío de fechas
   - ✏️ Modificado `saveEdit()` con validación y envío de fechas
   - ✏️ Agregados event listeners en `bindEvents()`

---

## 🎉 Conclusión

El sistema de vencimiento está **100% implementado en el frontend**. Los usuarios ahora pueden:

✅ Ingresar fechas de elaboración y vencimiento
✅ Ver fechas formateadas en la tabla
✅ Ver badges de estado con colores
✅ Filtrar productos por estado de vencimiento
✅ Recibir advertencias en tiempo real
✅ Prevenir errores (elaboración > vencimiento)

**Siguiente paso:** El usuario debe ejecutar la migración SQL en Supabase para que las columnas existan en la base de datos.
