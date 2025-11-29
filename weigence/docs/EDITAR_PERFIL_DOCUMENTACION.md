# 📝 Documentación: Edición de Perfil de Usuario

## ✨ Funcionalidades Implementadas

### 1. **Modal de Edición Rápida en el Sidebar**
- El botón **"Editar Perfil"** en el sidebar abre un modal sin salir de la página actual
- El modal incluye campos para:
  - ✅ Nombre completo (requerido)
  - ✅ Correo electrónico (opcional)
  - ✅ Número de celular (opcional, con formato +)
- Botones: **Guardar** y **Cancelar**

### 2. **Página de Edición Completa**
- Ruta: `/editar`
- Acceso: Mediante el botón "Editar Perfil" en el sidebar (también funciona directamente)
- Formulario completo con todos los campos
- Alertas visuales de éxito/error
- Validaciones en tiempo real

### 3. **Validaciones Implementadas**

#### Validación de Email ✉️
```
✅ Formato válido: usuario@dominio.com
✅ Soporta: números, letras, puntos, guiones, guión bajo
❌ Rechaza: espacios, caracteres especiales inválidos
```

#### Validación de Número de Celular ☎️
```
✅ Permitidos: dígitos (0-9), espacios, guiones (-), más (+), paréntesis ( )
✅ Asegura formato con + al inicio
✅ Ejemplos válidos:
   - +56 9 1234 5678 (celular Chile)
   - +56 22 1234 5678 (fijo Chile)
   - +56912345678 (sin espacios)
   - 912345678 (se convierte a +56912345678)
   - 56912345678 (se convierte a +56912345678)
❌ Rechaza: letras, caracteres especiales inválidos

FORMATEO AUTOMÁTICO:
- Input "912345678" → Guarda "+56912345678"
- Input "56912345678" → Guarda "+56912345678"
- Input "+56912345678" → Guarda "+56912345678"
- Input "+1 650 253 0000" → Guarda "+16502530000"
```

### 4. **API Endpoint**
- **Ruta**: `/api/editar-perfil`
- **Método**: POST (JSON)
- **Autenticación**: Requerida (@login_required)
- **Respuesta**: JSON con estado de la operación

**Ejemplo de solicitud:**
```json
POST /api/editar-perfil
Content-Type: application/json

{
  "nombre": "Juan Pérez",
  "email": "juan@ejemplo.com",
  "numero_celular": "+56 9 1234 5678"
}
```

**Respuesta exitosa:**
```json
{
  "success": true,
  "message": "Perfil actualizado correctamente",
  "usuario": {
    "nombre": "Juan Pérez",
    "email": "juan@ejemplo.com",
    "numero_celular": "+56912345678"
  }
}
```

### 5. **Actualización de Sesión y Base de Datos**
- Los cambios se guardan automáticamente en:
  - **Sesión**: `session['usuario_numero_celular']`
  - **Supabase**: Campo `numero_celular` en tabla `usuarios`
- Se actualiza:
  - `session['usuario_nombre']`
  - `session['usuario_correo']`
  - `session['usuario_numero_celular']`

## 🎨 Experiencia de Usuario

### Modal de Edición (Desde Sidebar)
```
1. Usuario hace clic en "Editar Perfil" en el sidebar
2. Modal se abre con un overlay oscuro
3. Campos precargan con información actual
4. Usuario realiza cambios
5. Validaciones en tiempo real muestran errores
6. Formato automático agrega "+" si no tiene
7. Al guardar:
   - Botón muestra "Guardando..." con icono de sincronización
   - Respuesta: ✅ Éxito o ❌ Error
   - Si éxito: Modal se cierra y página se recarga
```

### Página de Edición Completa
```
1. Usuario navega a /editar
2. Formulario con diseño completo
3. Mensajes de error/éxito arriba
4. Validaciones mostradas bajo cada campo
5. Botones: "Guardar cambios" y "Cancelar"
6. Número se formatea automáticamente con +
```

## 🛡️ Características de Seguridad

✅ **Autenticación obligatoria** (@login_required)
✅ **Validación del lado del servidor** (Python con regex)
✅ **Validación del lado del cliente** (JavaScript)
✅ **Sanitización de entrada** (strip, trim)
✅ **Formateo automático** (agrega + si falta)
✅ **Sesiones seguras** (HTTPONLY cookies)
✅ **Manejo de errores** (respuestas JSON)

## 📁 Archivos Modificados/Creados

### Creados:
- `app/templates/componentes/edit_profile_modal.html` - Modal de edición rápida
- `app/routes/perfil.py` - Backend completo con validaciones y API

### Modificados:
- `app/templates/pagina/editar.html` - Página de edición mejorada
- `app/templates/componentes/sidebar.html` - Botón que abre modal
- `app/templates/base.html` - Inclusión del modal

## 🔧 Funciones del Backend

### En `app/routes/perfil.py`:

```python
def validar_email(email):
    """Valida formato de correo electrónico"""
    # Retorna True si es válido
    
def validar_numero_celular(numero_celular):
    """Valida formato de número celular con +"""
    # Permite: dígitos, espacios, guiones, paréntesis y +
    # Retorna True si es válido

def formatear_numero_celular(numero_celular):
    """Formatea automáticamente el número celular"""
    # Agrega + si comienza con 56 o 9
    # Mantiene + si ya lo tiene
    # Retorna número formateado
    
@main.route('/editar', methods=['GET', 'POST'])
def editar():
    """Página de edición de perfil (formulario tradicional)"""
    
@main.route('/api/editar-perfil', methods=['POST'])
def api_editar_perfil():
    """API para edición rápida desde modal (JSON)"""
```

## 🎯 Casos de Uso

### Caso 1: Editar nombre y celular desde sidebar
```
1. Clic en "Editar Perfil" → Modal abre
2. Cambiar nombre y celular
3. Input celular: "912345678"
4. Clic en "Guardar"
5. ✅ Se formatea a "+56912345678"
6. Datos guardados en Supabase
7. Página se recarga automáticamente
```

### Caso 2: Cambiar email inválido
```
1. Modal abierto
2. Ingresar: "correo-invalido"
3. Al perder el foco: Mensaje de error rojo
4. Botón "Guardar" intenta enviar
5. ❌ Error: "El correo no tiene un formato válido"
6. Modal permanece abierto para corrección
```

### Caso 3: Número celular con formato incompleto
```
1. Usuario intenta escribir: "912345678"
2. Input filtra automáticamente caracteres inválidos
3. Al perder el foco: Valida formato
4. Al guardar: ✅ Se formatea a "+56912345678"
5. Se actualiza correctamente en Supabase
```

### Caso 4: Número internacional
```
1. Usuario ingresa: "+1 650 253 0000"
2. Input permite dígitos, espacios y +
3. Al guardar: ✅ Se guarda "+16502530000"
4. Funciona con cualquier código de país
```

## 📊 Validaciones Detalladas

### Email
```regex
^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
```
- Mínimo 2 caracteres después del punto
- Debe tener @ y dominio
- Soporta notación con puntos

### Número de Celular
```regex
^(\+?)[\d\s\-\(\)]+$
```
- Opcional: símbolo + al inicio
- Solo números: 0-9
- Espacios para separación
- Guiones: - 
- Paréntesis: ( )

## 🚀 Cómo Usar

### Para usuario final:
1. Haz clic en "Editar Perfil" en el sidebar
2. Modifica los campos que desees
3. El número celular se formatea automáticamente con +
4. Haz clic en "Guardar"
5. ¡Listo! Tus cambios se guardarán en Supabase

### Para desarrollador (API):
```javascript
const response = await fetch('/api/editar-perfil', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    nombre: 'Juan Pérez',
    email: 'juan@ejemplo.com',
    numero_celular: '+56 9 1234 5678'
  })
});
const data = await response.json();
if (data.success) {
  console.log('Perfil actualizado');
  console.log(data.usuario.numero_celular); // "+56912345678"
}
```

## 💡 Notas Importantes

1. **Campos opcionales**: Email y número celular son opcionales. Si se dejan vacíos, se guardan como `NULL` en Supabase.
2. **Formateo automático**: El número celular se formatea automáticamente con "+" al inicio
3. **Actualización en tiempo real**: La sesión se actualiza inmediatamente
4. **Recarga automática**: La página se recarga para reflejar cambios en toda la interfaz
5. **Diseño responsivo**: Modal y formulario se adaptan a dispositivos móviles
6. **Dark mode**: Completa compatibilidad con tema oscuro
7. **Campo Supabase**: Los datos se guardan en el campo `numero_celular` de la tabla `usuarios`

## 🔍 Troubleshooting

### Problema: El modal no se abre
- ✅ Solución: Verificar que `edit_profile_modal.html` esté incluido en `base.html`

### Problema: Los cambios no se guardan
- ✅ Solución: Verificar que Supabase está conectado correctamente
- ✅ Verificar permisos en la tabla `usuarios`
- ✅ Verificar que el campo es `numero_celular` (no `telefono`)

### Problema: Email válido se rechaza
- ✅ Solución: Usar formato correcto: `usuario@dominio.com`

### Problema: Número no se formatea con +
- ✅ Comportamiento esperado: El + se agrega automáticamente al guardar
- ✅ Verificar que el número comienza con 56, 9 u otro código de país

### Problema: No puedo escribir +
- ✅ Solución: El + se permite al inicio del campo
- ✅ Usa Ctrl+Shift+= en algunos teclados para escribir +

---

**Versión**: 2.0 (Actualizado para usar `numero_celular` con formato +)
**Última actualización**: 11 de noviembre de 2025
**Estado**: ✅ Funcional y completo

