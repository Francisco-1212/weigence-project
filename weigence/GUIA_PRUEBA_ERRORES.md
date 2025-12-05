# 🧪 GUÍA RÁPIDA: PRUEBA DEL SISTEMA DE REGISTRO DE ERRORES

## 📋 Pasos para Probar

### 1️⃣ Acceder a la Página de Pruebas

1. **Inicia el servidor** (si no está corriendo):
   ```bash
   cd weigence
   python app.py
   ```

2. **Abre tu navegador** y ve a:
   ```
   http://localhost:5000/test/errores
   ```

### 2️⃣ Generar Errores de Prueba

En la página verás varios botones:

#### **Errores de Frontend (JavaScript)**
- 🟠 **Error Normal**: Error de nivel normal
- 🟡 **Warning**: Advertencia
- 🔴 **Error Crítico**: Error crítico con stacktrace
- 💜 **Error con Exception**: Error real de JavaScript capturado
- 🛒 **Error de Ventas**: Simula error del módulo ventas
- 👥 **Error de Usuarios**: Simula error del módulo usuarios

#### **Errores de Backend (Python)**
- 🔧 **Error de Backend**: Error normal del servidor
- 💥 **Error Crítico Backend**: Error crítico con stacktrace (división por cero)

### 3️⃣ Verificar que se Registraron

#### **Opción A: Modal de Historial**
1. Haz clic en un botón de error
2. Ve al **footer** de la página
3. Haz clic en **"Ver historial"**
4. En el modal, selecciona la pestaña **"Errores"**
5. ✅ Deberías ver el error recién creado con:
   - Timestamp
   - Mensaje del error
   - Tu usuario
   - Nivel (error/warning/critical)

#### **Opción B: Página de Auditoría**
1. Haz clic en un botón de error
2. Ve a la página de **Auditoría**: http://localhost:5000/auditoria
3. Busca en la tabla eventos con:
   - Acción: `error_sistema_error`, `error_sistema_warning`, o `error_sistema_critical`
   - Detalle: Mensaje del error que generaste
   - Usuario: Tu usuario actual
   - Fecha: Hace unos segundos

#### **Opción C: Consola del Navegador**
1. Abre la consola del navegador (F12)
2. Haz clic en un botón de error
3. Verás el log en la consola con el mensaje del error
4. También verás confirmación de envío en el "Log de Resultados" en la misma página

### 4️⃣ Probar Errores Reales

Para ver errores reales en acción:

1. **Error en Ventas**:
   - Ve a la página de Ventas
   - Intenta guardar una venta sin productos
   - El error se registrará automáticamente

2. **Error en Usuarios**:
   - Ve a Gestión de Usuarios
   - Intenta crear un usuario con datos inválidos
   - El error se registrará automáticamente

3. **Error en Inventario**:
   - Ve a Movimientos de Inventario
   - Intenta crear un movimiento inválido
   - El error se registrará automáticamente

## 🔍 Estructura de los Errores Registrados

Cada error en la tabla `auditoria_eventos` tiene:

```json
{
  "fecha": "2025-12-04T15:30:45.123456",
  "usuario": "admin@weigence.cl",
  "accion": "error_sistema_critical",
  "detalle": "[test] Error crítico de prueba. Este es un error CRÍTICO de prueba"
}
```

### Niveles de Error:
- **error_sistema_error**: Errores normales
- **error_sistema_warning**: Advertencias
- **error_sistema_critical**: Errores críticos (incluyen stacktrace)

## ✅ Resultado Esperado

Después de generar errores, deberías poder:
- ✅ Verlos en el modal de historial (pestaña "Errores")
- ✅ Verlos en la página de Auditoría
- ✅ Ver confirmación en el "Log de Resultados" de la página de prueba
- ✅ Ver logs en la consola del navegador
- ✅ (Backend) Ver logs en la consola del servidor

## 🎯 Quick Test (5 segundos)

1. Ve a: `http://localhost:5000/test/errores`
2. Haz clic en **"🔴 Error Crítico"**
3. Haz clic en **"Ver historial"** (footer)
4. Selecciona pestaña **"Errores"**
5. ✅ Deberías ver tu error registrado

---

**¡Listo!** El sistema de registro de errores está funcionando correctamente. 🎉
