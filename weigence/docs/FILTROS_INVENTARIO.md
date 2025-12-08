# Sistema de Filtros Avanzados - Inventario

## Resumen de Implementación

Se ha implementado un sistema completo de filtros para la sección de inventario, permitiendo filtrar y ordenar productos de manera eficiente.

## Características Implementadas

### 1. Panel de Filtros Desplegable
- Botón "Filtros" con icono que muestra/oculta el panel
- Icono de chevron que rota al abrir/cerrar
- Panel contraible que no interfiere con el resto de la UI

### 2. Filtros Disponibles

#### Filtro por Estado de Stock
- **Todos**: Muestra todos los productos
- **Sin Stock**: Productos con stock = 0
- **Bajo Stock**: Productos con stock entre 1 y 9
- **Normal**: Productos con stock >= 10

#### Filtro por Estante
- Selector dropdown con todos los estantes disponibles
- Opción "Todos los estantes" para limpiar el filtro
- Usa los códigos de estante formateados (E1-A, E2-B, etc.)

#### Filtro por Categoría
- Selector dropdown con todas las categorías disponibles
- Opción "Todas las categorías" para limpiar el filtro
- Lista dinámica basada en las categorías existentes

#### Ordenamiento por Vencimiento
- **Sin ordenar**: Orden por defecto (estante, categoría, nombre)
- **Más cercano primero**: Productos próximos a vencer aparecen primero
- **Más lejano primero**: Productos con vencimiento lejano aparecen primero
- Los productos sin fecha de vencimiento aparecen al final

### 3. Funcionalidades Adicionales

#### Botón Limpiar Filtros
- Resetea todos los filtros a su estado inicial
- Restaura la vista "Todos" en el filtro de estado
- Limpia los selectores de estante y categoría
- Elimina el ordenamiento por vencimiento

#### Sistema de Filtros Combinados
- Todos los filtros funcionan simultáneamente
- Filtrado en tiempo real al cambiar cualquier selector
- Paginación automática después de aplicar filtros

## Estructura de Archivos Modificados

### Backend (Python)
**Archivo**: `weigence/app/routes/inventario.py`
- Agregado `codigo_estante` formateado a cada producto
- Se usa `estantes_catalogo` para formatear los códigos

### Frontend (HTML)
**Archivo**: `weigence/app/templates/pagina/inventario.html`
- Nuevo botón "Filtros" con toggle
- Panel de filtros contraible con `id="panelFiltros"`
- Selectores para estante, categoría y ordenamiento
- Botón "Limpiar Filtros"
- Mantiene los data-attributes necesarios en las filas

### Frontend (JavaScript)
**Archivo**: `weigence/app/static/js/inventario.js`

#### Nuevos elementos en state:
```javascript
filters: {
  category: '',
  status: '',
  estante: '',
  ordenVencimiento: ''
}
```

#### Nuevos métodos:
- `aplicarFiltrosCompletos()`: Aplica todos los filtros simultáneamente
- `ordenarPorVencimiento(rows, orden)`: Ordena las filas por fecha de vencimiento
- `limpiarFiltros()`: Resetea todos los filtros

#### Métodos modificados:
- `filterByStatus()`: Ahora usa el sistema unificado de filtros
- `cacheDOM()`: Incluye los nuevos elementos del DOM
- `bindEvents()`: Agrega event listeners para los nuevos controles

## Data Attributes Utilizados

Cada fila de producto (`<tr class="product-row">`) tiene los siguientes atributos:
- `data-stock`: Cantidad en stock
- `data-category`: Categoría del producto
- `data-estante`: Código del estante (E1-A, E2-B, etc.)
- `data-fecha-venc`: Fecha de vencimiento (formato ISO)
- `data-vencimiento`: Estado del vencimiento (vencido, critico, proximo, vigente)

## Estilo Visual

- Diseño consistente con el resto de la aplicación
- Modo claro/oscuro completamente soportado
- Responsive en todos los tamaños de pantalla
- Transiciones suaves al abrir/cerrar el panel
- Sin emojis, solo iconos de Material Symbols

## Uso

1. **Abrir Panel de Filtros**: Click en el botón "Filtros"
2. **Aplicar Filtros**: Seleccionar opciones en los dropdowns
3. **Ordenar**: Elegir orden de vencimiento si es necesario
4. **Limpiar**: Click en "Limpiar Filtros" para resetear todo

## Compatibilidad

- Compatible con todos los navegadores modernos
- Funciona con la paginación existente
- No interfiere con la búsqueda por texto
- Se integra con el sistema de exportación a Excel
