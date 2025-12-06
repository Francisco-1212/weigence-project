# 🎨 Control Inteligente - Guía Visual de Cambios

## 📊 Dashboard View (Nivel 1)

### Mensaje Contextual Dinámico

**ANTES:**
```
✓ Sistema saludable
No se detectaron problemas en este momento.
```

**DESPUÉS (con hallazgos críticos):**
```html
<⚠️ icon animado> Atención urgente: Problemas críticos detectados

⚠️ STOCK CRÍTICO: Paracetamol 500mg está completamente agotado, 
lo que impide ventas inmediatas. Se detectaron 3 problemas críticos 
que requieren acción inmediata. Haz click en la tarjeta roja para 
revisar y resolver.
```

**DESPUÉS (con hallazgos de oportunidad):**
```html
<💡 icon> Oportunidades de mejora disponibles

🏆 TOP VENTAS: Ibuprofeno 400mg está liderando el catálogo. 
Hay 2 oportunidades de optimización detectadas. Haz click en 
la tarjeta azul para explorar.
```

---

## 🔍 Detail View (Nivel 2)

### Pestaña CONTEXTO

**Campo: Descripción**

**ANTES:**
```
Producto completamente agotado. Impacto directo en disponibilidad y ventas.
```

**DESPUÉS (con datos de audit trail):**
```
Producto completamente agotado. Impacto directo en disponibilidad y ventas. 
| 📊 Alta actividad detectada: 15 eventos en la última hora. 3 usuarios 
involucrados: Juan Pérez, María García, Carlos López. 🚨 5 alertas de 
stock generadas recientemente.
```

---

### Pestaña DIAGNÓSTICO

**Métricas Detectadas**

**ANTES:**
```
┌─────────┐  ┌─────────┐  ┌─────────┐
│ 🔼      │  │ 📊      │  │ ⚡      │
│ 47      │  │ 62%     │  │ Crítico │
└─────────┘  └─────────┘  └─────────┘
```

**DESPUÉS (Stock cero de "Paracetamol"):**
```
┌─────────┐  ┌─────────┐  ┌──────────┐
│ 🔼      │  │ 📊      │  │ ⚡       │
│ 0u      │  │ 95%     │  │ Sin Stock│
└─────────┘  └─────────┘  └──────────┘
```

**DESPUÉS (Alta demanda, 150u vendidas):**
```
┌──────────┐  ┌─────────┐  ┌─────────┐
│ 🔼       │  │ 📊      │  │ ⚡      │
│ 150 unid.│  │ 25%     │  │ Top     │
└──────────┘  └─────────┘  └─────────┘
```

**DESPUÉS (4h sin movimientos):**
```
┌─────────┐  ┌─────────┐  ┌─────────┐
│ 🔼      │  │ 📊      │  │ ⚡      │
│ 4.0h    │  │ 75%     │  │ Parado  │
└─────────┘  └─────────┘  └─────────┘
```

---

### Pestaña RESOLUCIÓN

**Pasos Sugeridos**

**ANTES (sin enlaces):**
```
┌───────────────────────────────────────┐
│ [1] Revisar el evento en el módulo... │
│ [2] Generar orden de reposición...    │
│ [3] Monitorear la evolución...        │
└───────────────────────────────────────┘
```

**DESPUÉS (con rutas reales):**
```
┌──────────────────────────────────────────┐
│ [1] Abrir módulo de Inventario      [→] │ ← Hover azul + flecha
│ [2] Generar orden de reposición...      │
│ [3] Verificar niveles de stock...   [→] │ ← Hover azul + flecha
│ [4] Documentar acciones tomadas...      │
└──────────────────────────────────────────┘
```

---

## 🎮 Footer de Navegación

**ANTES:**
```
┌─────────────────────────────────────────┐
│ [< Anterior]  |  Hallazgo 1 de 6  | [Siguiente >] │
└─────────────────────────────────────────┘
```
- Botones en extremos (justify-between)
- Texto "Anterior/Siguiente" oculto en móvil

**DESPUÉS:**
```
┌──────────────────────────────────────────┐
│      [< Anterior]  | 📊 1 / 6 |  [Siguiente >]      │
└──────────────────────────────────────────┘
```
- **Centrado** (justify-center con gap-4)
- Botones más grandes (px-4 py-2.5)
- Border doble (border-2)
- Hover azul con shadow
- Disabled con opacidad 40%
- Texto siempre visible
- Contador con gradiente dual (azul/morado)

**Estados visuales:**

1. **Normal:**
   ```
   [< Anterior]  →  bg-white, border-gray-300
   ```

2. **Hover:**
   ```
   [< Anterior]  →  bg-blue-50, border-blue-500, shadow-md
   ```

3. **Disabled (primer hallazgo):**
   ```
   [< Anterior]  →  opacity-40, sin hover
   ```

---

## 🎨 Paleta Semántica de Severidad

### Critical (Crítico)
```
Color primario: #ef4444
Gradiente: from-red-500 to-red-600
Barra: 100% ancho
Badge: bg-red-500/20, text-red-600, border-red-500/40
```

### High (Advertencia)
```
Color primario: #f97316
Gradiente: from-yellow-500 to-amber-600
Barra: 75% ancho
Badge: bg-orange-500/20, text-orange-600, border-orange-500/40
```

### Medium (Oportunidad)
```
Color primario: #f59e0b
Gradiente: from-blue-500 to-cyan-600
Barra: 50% ancho
Badge: bg-blue-500/20, text-blue-600, border-blue-500/40
```

### Low (Información)
```
Color primario: #10b981
Gradiente: from-green-500 to-emerald-600
Barra: 25% ancho
Badge: bg-green-500/20, text-green-600, border-green-500/40
```

---

## 🔄 Flujo de Usuario

### Escenario 1: Stock Crítico

1. **Dashboard (Nivel 1)**
   ```
   [Mensaje] ⚠️ STOCK CRÍTICO: Paracetamol está completamente agotado
   
   [Card Crítico] 
   🚨 Crítico - 3 problemas
   ```

2. **Click en Card Crítico**
   ```
   → Transición a Detail View
   → Filtro aplicado: severity = "critical"
   → Hallazgos filtrados: 3 items
   ```

3. **Detail View (Nivel 2)**
   ```
   [Breadcrumb] Dashboard / Crítico
   
   [Pestaña Contexto]
   Título: Stock cero: "Paracetamol 500mg"
   Descripción: [ENRIQUECIDA CON AUDIT TRAIL]
   Módulo: Inventario [→]
   
   [Pestaña Diagnóstico]
   Métricas: 0u | 95% | Sin Stock
   
   [Pestaña Resolución]
   Pasos:
   1. Abrir módulo de Inventario [→]
   2. Generar orden de reposición...
   3. Verificar niveles de stock [→]
   ```

4. **Click en "Abrir módulo de Inventario"**
   ```
   → window.location.href = '/inventario'
   ```

---

## 📱 Responsive Behavior

### Mobile (< 640px)
- Tabs: Texto corto ("Info", "Diag", "Plan")
- Métricas: Grid 3 columnas compactas
- Navegación: Texto siempre visible (ya no se oculta)

### Desktop (≥ 640px)
- Tabs: Texto completo ("Contexto", "Diagnóstico", "Resolución")
- Métricas: Grid 3 columnas con más padding
- Navegación: Botones más espaciados

---

## 🌓 Dark Mode

### Dashboard Cards
```css
/* Light */
bg-gradient-to-br from-red-500/5 to-red-600/5
border-red-500/30

/* Dark */
dark:border-red-500/40
dark:hover:bg-red-500/10
```

### Detail View Panels
```css
/* Light */
bg-blue-50
border-blue-200

/* Dark */
dark:bg-blue-500/10
dark:border-blue-500/30
```

### Navigation Buttons
```css
/* Light */
bg-white
border-gray-300
hover:bg-blue-50

/* Dark */
dark:bg-neutral-700
dark:border-neutral-600
dark:hover:bg-blue-500/10
```

---

**Documento generado por GitHub Copilot**  
*Última actualización: 2025-01-21*
