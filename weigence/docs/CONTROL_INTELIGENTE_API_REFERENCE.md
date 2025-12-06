# 🔧 Control Inteligente - Referencia Técnica de APIs

## 📡 Funciones JavaScript Exportadas

### `recomendaciones.js`

#### 1. `generarContextoEspecifico(hallazgo)`

**Descripción:** Genera un mensaje contextual corto basado en el tipo de hallazgo.

**Parámetros:**
```typescript
hallazgo: {
  modulo: 'inventario' | 'ventas' | 'movimientos' | 'alertas' | 'auditoria',
  titulo: string,
  descripcion: string,
  ml_severity: 'critical' | 'high' | 'medium' | 'low'
}
```

**Retorna:** `string` - Mensaje contextual o vacío si no aplica

**Ejemplo:**
```javascript
const hallazgo = {
  modulo: 'inventario',
  titulo: 'Stock cero: "Paracetamol 500mg"',
  descripcion: '...',
  ml_severity: 'critical'
};

generarContextoEspecifico(hallazgo);
// → "⚠️ STOCK CRÍTICO: Paracetamol 500mg está completamente agotado, lo que impide ventas inmediatas."
```

**Mapeo de patrones:**
| Módulo | Patrón en título | Contexto generado |
|--------|------------------|-------------------|
| inventario | `stock cero` o `agotado` | ⚠️ STOCK CRÍTICO: [producto]... |
| inventario | `sobrecarga` o `sobrecapacidad` | ⚖️ SOBREPESO: Se detectó exceso... |
| ventas | `alta demanda` o `líder` | 🏆 TOP VENTAS: [producto]... |
| movimientos | `anomalía` o `sin justificar` | 🔍 ANOMALÍA: Movimientos sin... |
| auditoria | `patrón` o `anómala` | 🛡️ COMPORTAMIENTO ATÍPICO... |

---

#### 2. `enriquecerDescripcionConAuditoria(hallazgo)`

**Descripción:** Enriquece la descripción del hallazgo con datos del Live Audit Trail.

**Parámetros:**
```typescript
hallazgo: {
  modulo: string,
  descripcion: string
}
```

**Retorna:** `Promise<string>` - Descripción enriquecida

**Dependencias:**
- `window.state.logs` (array de logs del audit trail)

**Análisis realizado:**
1. Filtra eventos de última hora relevantes al módulo
2. Cuenta eventos relacionados
3. Extrae usuarios únicos involucrados
4. Detecta patrones específicos por módulo

**Ejemplo:**
```javascript
await enriquecerDescripcionConAuditoria({
  modulo: 'inventario',
  descripcion: 'Stock agotado'
});

// Con 15 eventos, 3 usuarios, 5 alertas:
// → "Stock agotado | 📊 Alta actividad detectada: 15 eventos en la última hora. 
//    3 usuarios involucrados: Juan, María, Carlos. 🚨 5 alertas de stock generadas."
```

**Mapeo módulo → eventos:**
```javascript
{
  'inventario': ['movimientos_inventario', 'alertas_stock'],
  'ventas': ['ventas', 'detalle_ventas'],
  'movimientos': ['movimientos_inventario', 'retiros_programados', 'retiros_fuera_de_horario'],
  'alertas': ['alertas_sistema', 'alertas_stock', 'errores_criticos'],
  'auditoria': ['login_logout_usuarios', 'gestion_usuarios', 'modificacion_datos']
}
```

---

#### 3. `calcularMetricasReales(hallazgo)`

**Descripción:** Calcula métricas precisas basadas en el hallazgo.

**Parámetros:**
```typescript
hallazgo: {
  modulo: string,
  ml_severity: 'critical' | 'high' | 'medium' | 'low',
  titulo: string,
  descripcion: string
}
```

**Retorna:**
```typescript
{
  metric1: string,  // Frecuencia/Cantidad
  metric2: string,  // Impacto/Porcentaje
  metric3: string   // Estado/Categoría
}
```

**Ejemplo:**
```javascript
calcularMetricasReales({
  modulo: 'inventario',
  titulo: 'Stock cero: "Paracetamol"',
  descripcion: 'Stock actual: 0 unidades',
  ml_severity: 'critical'
});

// → { metric1: '0u', metric2: '95%', metric3: 'Sin Stock' }
```

**Lógica Metric 1:**
- Extrae primer número del texto con regex: `/(\d+(?:\.\d+)?)/`
- Formatea según contexto:
  - Inventario + stock → `[N]u`
  - Ventas → `[N] unid.`
  - Inactividad → `[N]h`
  - Otro → `[N]`

**Lógica Metric 2:**
- Busca `%` explícito en descripción
- Fallback por severidad: critical=95%, high=75%, medium=50%, low=25%

**Lógica Metric 3:**
- Prioridad: Patrón en título → Estado por severidad
- Inventario: `Sin Stock`, `Exceso`, `Reorden`
- Ventas: `Top`, `Bajo`
- Movimientos: `Revisar`, `Parado`

---

#### 4. `generarPasosAccion(planAccion, hallazgo)`

**Descripción:** Genera lista de pasos accionables con rutas.

**Parámetros:**
```typescript
planAccion: string,
hallazgo: {
  modulo: string,
  ml_severity: string,
  plan_accion?: string
}
```

**Retorna:**
```typescript
Array<{
  text: string,
  route: string | null
}>
```

**Ejemplo:**
```javascript
generarPasosAccion(
  "Generar orden. Verificar stock.", 
  { modulo: 'inventario', ml_severity: 'critical' }
);

// → [
//   { text: "Abrir módulo de Inventario", route: "/inventario" },
//   { text: "Generar orden", route: null },
//   { text: "Verificar niveles de stock y configurar alertas", route: "/inventario" },
//   { text: "Documentar acciones tomadas y monitorear resultados", route: null }
// ]
```

**Generación automática:**
- Si `planAccion` no tiene pasos claros → Llama `generarPasosContextuales()`
- Si tiene pasos → Los parsea + detecta rutas con `detectarRutaEnPaso()`

---

#### 5. `generarPasosContextuales(hallazgo, planOriginal)`

**Descripción:** Genera pasos específicos por módulo (fallback).

**Estructura fija:**
1. **Paso 1:** Navegación al módulo afectado (siempre con ruta)
2. **Paso 2:** Plan original o acción genérica
3. **Paso 3:** Acción específica por módulo (con ruta)
4. **Paso 4:** Monitoreo (solo si critical/high)

**Mapeo módulo → Paso 3:**
```javascript
{
  inventario: "Verificar niveles de stock y configurar alertas",
  ventas: "Analizar tendencias y patrones de venta",
  movimientos: "Revisar historial y justificar movimientos",
  alertas: "Resolver alertas pendientes y configurar notificaciones",
  auditoria: "Revisar registros de auditoría y patrones de usuarios"
}
```

---

#### 6. `detectarRutaEnPaso(texto, hallazgo)`

**Descripción:** Detecta rutas en texto mediante palabras clave.

**Parámetros:**
```typescript
texto: string,
hallazgo: { modulo: string }
```

**Retorna:** `string | null`

**Palabras clave → Rutas:**
```javascript
{
  'inventario' | 'stock': '/inventario',
  'venta' | 'ventas': '/ventas',
  'movimiento' | 'retiro': '/movimientos',
  'alerta': '/alertas',
  'auditor' | 'usuario': '/auditoria',
  'dashboard' | 'panel': '/dashboard'
}
```

---

#### 7. `actualizarMensajeContextual(counts)`

**Descripción:** Actualiza mensaje del dashboard según conteo de severidades.

**Parámetros:**
```typescript
counts: {
  critical: number,
  high: number,
  medium: number,
  low: number
}
```

**Efecto:** Modifica DOM (`elements.dashboardContextTitle` y `elements.dashboardContextMessage`)

**Lógica de priorización:**
1. Si `critical > 0` → Mensaje urgente con icono `warning` animado
2. Si `high > 0` → Mensaje de advertencia con icono `priority_high`
3. Si `medium > 0` → Mensaje de oportunidad con icono `lightbulb`
4. Si `low > 0` → Mensaje informativo con icono `info`
5. Si todos en 0 → Mensaje de sistema saludable con icono `check_circle`

**Enriquecimiento:**
- Llama `generarContextoEspecifico()` con hallazgo de mayor prioridad
- Inserta contexto específico al inicio del mensaje

---

## 🗂️ Estructura de Datos

### Hallazgo ML (Backend)

```typescript
interface Hallazgo {
  emoji: string;              // '🚨', '⚠️', '💡', etc.
  modulo: 'dashboard' | 'inventario' | 'movimientos' | 'ventas' | 'alertas' | 'auditoria';
  titulo: string;             // "Stock cero: "Paracetamol 500mg""
  descripcion: string;        // Descripción detallada
  ml_severity: 'critical' | 'high' | 'medium' | 'low';
  plan_accion: string;        // Pasos sugeridos en texto
}
```

**Generado en:** `app/ia/ia_ml_anomalies.py` → Función `generate_findings_for_carousel()`

---

### Log de Auditoría (Live Audit Trail)

```typescript
interface AuditLog {
  id: number;
  timestamp: string;          // ISO 8601 UTC
  fecha: string;              // 'YYYY-MM-DD'
  hora: string;               // 'HH:MM:SS'
  mensaje: string;
  detalle: string;
  usuario: string;
  rut: string;
  producto?: string;
  estante?: string;
  tipo_evento: string;        // Ver mapeo abajo
  nivel: 'INFO' | 'WARN' | 'CRIT';
  nivelClass: string;
}
```

**Tipos de eventos:**
- `login_logout_usuarios`
- `ventas`
- `detalle_ventas`
- `movimientos_inventario`
- `retiros_programados`
- `retiros_fuera_de_horario`
- `alertas_sistema`
- `alertas_stock`
- `errores_criticos`
- `gestion_usuarios`
- `modificacion_datos`

---

## 🎨 Configuración de Colores

### `SEVERITY_CONFIG`

```javascript
{
  low: { 
    label: 'Baja', 
    color: '#10b981',    // green-500
    width: '25%' 
  },
  medium: { 
    label: 'Media', 
    color: '#f59e0b',    // yellow-500
    width: '50%' 
  },
  high: { 
    label: 'Alta', 
    color: '#f97316',    // orange-500
    width: '75%' 
  },
  critical: { 
    label: 'Crítica', 
    color: '#ef4444',    // red-500
    width: '100%' 
  }
}
```

### `MODULE_ICONS`

```javascript
{
  dashboard: 'dashboard',
  inventario: 'inventory_2',
  movimientos: 'swap_horiz',
  ventas: 'point_of_sale',
  alertas: 'notifications_active',
  auditoria: 'shield'
}
```

### `MODULE_ROUTES`

```javascript
{
  dashboard: '/dashboard',
  inventario: '/inventario',
  movimientos: '/movimientos',
  ventas: '/ventas',
  alertas: '/alertas',
  auditoria: '/auditoria'
}
```

---

## 🔄 Flujo de Datos

### 1. Carga Inicial

```mermaid
cargarRecomendacion('auditoria')
  → fetch('/api/recomendacion/auditoria')
  → payload.data = { ml_insights_cards: [...] }
  → normalizar(payload.data)
  → aplicarCard(data)
    → mostrarResumenSeveridad(ml_insights_cards)
      → actualizarMensajeContextual(counts)
        → generarContextoEspecifico(hallazgoMasPrioritario)
    → mostrarVista('dashboard')
```

### 2. Click en Severity Card

```mermaid
severityCard.click()
  → filtrarPorSeveridad(severity)
    → state.filteredHallazgos = mlHallazgos.filter(...)
    → mostrarVista('detail')
    → mostrarHallazgoFiltrado(0)
      → mostrarHallazgo(hallazgo, index, total)
        → enriquecerDescripcionConAuditoria(hallazgo)
        → calcularMetricasReales(hallazgo)
        → generarPasosAccion(hallazgo.plan_accion, hallazgo)
```

### 3. Navegación de Hallazgos

```mermaid
navNext.click()
  → mostrarHallazgoFiltrado(index + 1)
    → mostrarHallazgo(nextHallazgo, index, total)
```

---

## 🧪 Testing con Datos Mock

### Crear hallazgo de prueba:

```javascript
const mockHallazgo = {
  emoji: '🚨',
  modulo: 'inventario',
  titulo: 'Stock cero: "Paracetamol 500mg"',
  descripcion: 'Producto completamente agotado. Stock actual: 0 unidades.',
  ml_severity: 'critical',
  plan_accion: 'Generar orden de reposición. Contactar proveedor prioritario.'
};
```

### Inyectar en estado:

```javascript
// En consola de navegador:
window.state.logs = [
  {
    timestamp: new Date().toISOString(),
    tipo_evento: 'alertas_stock',
    usuario: 'Juan Pérez',
    detalle: 'Stock bajo: Paracetamol'
  },
  // ... más logs
];

// Forzar re-renderizado
mostrarHallazgo(mockHallazgo, 0, 1);
```

### Verificar enriquecimiento:

```javascript
await enriquecerDescripcionConAuditoria(mockHallazgo);
// Debería incluir: "| 📊 ... eventos en la última hora"
```

---

## 📊 Performance

### Complejidad Temporal

| Función | Complejidad | Notas |
|---------|-------------|-------|
| `generarContextoEspecifico` | O(1) | Solo string matching |
| `enriquecerDescripcionConAuditoria` | O(n) | n = logs en última hora |
| `calcularMetricasReales` | O(1) | Regex + lookup |
| `generarPasosAccion` | O(m) | m = cantidad de pasos |
| `detectarRutaEnPaso` | O(1) | Lookup en objeto |

### Optimizaciones Aplicadas

1. **Filtro temporal previo**: Solo procesa logs de última hora (reduce dataset)
2. **Set para usuarios únicos**: Evita duplicados en O(1)
3. **Early return**: Si no hay `window.state.logs`, retorna descripción original
4. **Lazy evaluation**: Solo enriquece al mostrar detail view (no en dashboard)

---

## 🐛 Debugging

### Console Logs Importantes

```javascript
// Al cargar hallazgos
console.log('[IA-CARD] Datos RAW recibidos:', raw);
console.log('[IA-CARD] Datos normalizados:', normalizado);

// Al mostrar hallazgo
console.log('[IA-CARD] Mostrando hallazgo:', hallazgo);

// En enriquecimiento
console.log('[IA-CARD] Eventos relacionados:', eventosRelacionados);
console.log('[IA-CARD] Usuarios únicos:', Array.from(usuariosUnicos));
```

### Verificar Estado Global

```javascript
// En consola del navegador:
window.state.logs          // Logs del audit trail
elements.mlHallazgos       // Hallazgos ML cargados
state.currentFilter        // Filtro de severidad actual
state.filteredHallazgos    // Hallazgos filtrados
```

---

**Documento generado por GitHub Copilot**  
*Última actualización: 2025-01-21*
