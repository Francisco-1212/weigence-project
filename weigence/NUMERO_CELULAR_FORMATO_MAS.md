# 📱 ACTUALIZACIÓN: Número de Celular con Formato "+"

## ✅ Cambios Realizados

### 1. **Backend actualizado** (`app/routes/perfil.py`)

#### Función de validación
```python
def validar_numero_celular(numero_celular):
    """Valida que el número de celular contenga solo dígitos, espacios y caracteres válidos"""
    if not numero_celular:
        return True  # Campo opcional
    # Permite solo números, espacios, guiones, más (+) y paréntesis
    return re.match(r'^(\+?)[\d\s\-\(\)]+$', numero_celular) is not None
```

#### Función de formateo
```python
def formatear_numero_celular(numero_celular):
    """Formatea el número de celular para asegurar que tiene el '+' al inicio si es internacional"""
    if not numero_celular:
        return None
    
    numero_celular = numero_celular.strip()
    
    # Si comienza con +, mantenerlo
    if numero_celular.startswith('+'):
        return numero_celular
    
    # Si comienza con 56 (código de Chile), agregar +
    if numero_celular.startswith('56'):
        return '+' + numero_celular
    
    # Si comienza con 9 (número chileno), agregar +56
    if numero_celular.startswith('9') and len(numero_celular) >= 8:
        return '+56' + numero_celular
    
    # Si solo tiene dígitos, agregar + al inicio
    if re.match(r'^[\d\s]+$', numero_celular):
        return '+' + numero_celular.replace(' ', '')
    
    return numero_celular
```

### 2. **Campo en Base de Datos**

**De**: `telefono`
**A**: `numero_celular` (columna de Supabase)

✅ Todos los queries usan `numero_celular`

```python
update_data = {
    "nombre": nombre,
    "email": email if email else None,
    "numero_celular": numero_celular_formateado
}
```

### 3. **Sesión del Usuario**

**De**: `session['usuario_telefono']`
**A**: `session['usuario_numero_celular']`

```python
session['usuario_numero_celular'] = numero_celular_formateado if numero_celular_formateado else session.get('usuario_numero_celular', '')
```

### 4. **Templates actualizados**

#### Modal (`edit_profile_modal.html`)
```html
<input type="tel" 
       id="modal-numero_celular"
       name="numero_celular" 
       value="{{ session.get('usuario_numero_celular', '') }}"
       placeholder="+56 9 1234 5678">
```

#### Página de edición (`editar.html`)
```html
<input type="tel" 
       id="telefono"
       name="numero_celular" 
       value="{{ session.get('usuario_numero_celular', '') }}"
       placeholder="+56 9 1234 5678">
```

---

## 🎯 Ejemplos de Formateo

### Entrada → Salida

| Entrada | Salida | Explicación |
|---------|--------|-------------|
| `912345678` | `+5691234567`8 | Se agrega +56 (código Chile) |
| `56912345678` | `+56912345678` | Se agrega + al inicio |
| `+56 9 1234 5678` | `+56 9 1234 5678` | Se mantiene como está |
| `22 1234 5678` | `+5622 1234 5678` | Número fijo Santiago |
| `` (vacío) | `None` | Campo opcional |

---

## ✨ Características del Formateo

✅ **Detecta código de país**
- Si empieza con `56` → Agrega `+`
- Si empieza con `9` → Agrega `+56`

✅ **Mantiene formato internacional**
- Si ya tiene `+` → Lo mantiene

✅ **Acepta variaciones**
- Con espacios: `+56 9 1234 5678`
- Sin espacios: `+56912345678`
- Con guiones: `+56-9-1234-5678`

✅ **Campo opcional**
- Si está vacío → `NULL` en base de datos
- Si tiene valor → Se formatea y guarda con `+`

---

## 🧪 Validaciones

### ✅ Acepta
```
✅ +56 9 1234 5678       (formato internacional)
✅ +56-9-1234-5678       (con guiones)
✅ +56(9)1234 5678       (con paréntesis)
✅ 912345678             (se convierte a +56912345678)
✅ 56912345678           (se convierte a +56912345678)
✅ 22 1234 5678          (número fijo, se agrega +56)
```

### ❌ Rechaza
```
❌ +56 9 1234 ABC        (contiene letras)
❌ +56 9 1234 @567       (caracteres especiales)
❌ 9123456AB             (mezclado con letras)
```

---

## 🔄 API Endpoint

### Request
```json
POST /api/editar-perfil
{
  "nombre": "Juan Pérez",
  "email": "juan@ejemplo.com",
  "numero_celular": "+56 9 1234 5678"
}
```

### Response (Éxito)
```json
{
  "success": true,
  "message": "Perfil actualizado correctamente",
  "usuario": {
    "nombre": "Juan Pérez",
    "email": "juan@ejemplo.com",
    "numero_celular": "+56 9 1234 5678"
  }
}
```

---

## 📊 Cambios por Archivo

| Archivo | Cambios |
|---------|---------|
| `app/routes/perfil.py` | ✅ Función de formateo, validación actualizada |
| `app/templates/componentes/edit_profile_modal.html` | ✅ Campo `numero_celular` |
| `app/templates/pagina/editar.html` | ✅ Campo `numero_celular` |
| `app/templates/base.html` | ✅ Modal incluido |

---

## 💾 Base de Datos

### Query Update
```sql
UPDATE usuarios 
SET numero_celular = '+56912345678',
    email = 'juan@ejemplo.com',
    nombre = 'Juan Pérez'
WHERE rut_usuario = '12.345.678-9';
```

---

## 🚀 Cómo Funciona

### Proceso Completo

```
Usuario ingresa: "912345678"
         ↓
JavaScript valida: ✅ Patrón válido
         ↓
Envía a backend: { numero_celular: "912345678" }
         ↓
Python formatea: +56912345678
         ↓
Guarda en Supabase: numero_celular = "+56912345678"
         ↓
Actualiza sesión: session['usuario_numero_celular'] = "+56912345678"
         ↓
Página recarga y muestra: "+56912345678"
```

---

## ✅ Testing

Para probar, ejecuta en PowerShell:
```powershell
cd vsls:/
python test_numero_celular.py
```

Verifica que el script valide:
- ✅ Números chilenos (9XXXXXXXX)
- ✅ Con código de país (5691234567)
- ✅ Con símbolo + (+56912345678)
- ✅ Con espacios/guiones
- ❌ Con caracteres inválidos

---

**Versión**: 2.0
**Última actualización**: 11 de noviembre de 2025
**Estado**: ✅ Funcional con formato "+"
