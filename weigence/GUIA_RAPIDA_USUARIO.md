# 🎯 GUÍA RÁPIDA: Editar tu Perfil

## 👤 ¿Cómo editar mi perfil?

### Opción 1️⃣: Modal Rápida (Recomendado ⚡)

```
1. Busca el botón "Editar Perfil" en el sidebar
2. Click en él → Se abre una ventana emergente
3. Modifica lo que quieras:
   • Nombre: Campo requerido
   • Correo: Opcional, formato: usuario@dominio.com
   • Celular: Opcional, formato: +56 9 XXXX XXXX
4. Click en "Guardar" ✅
5. ¡Listo! Tu perfil está actualizado
```

### Opción 2️⃣: Página Completa

```
1. Ve a: http://localhost:5000/editar
2. Completa el formulario
3. Click en "Guardar cambios"
4. ¡Listo! Cambios guardados
```

---

## 📝 Campos Disponibles

### Nombre Completo ⭐
```
✅ Requerido (no puede estar vacío)
✅ Ejemplo: "Juan Pérez"
✅ Máximo: 255 caracteres
```

### Correo Electrónico 📧
```
❌ Opcional (puedes dejar vacío)
✅ Formato: usuario@dominio.com
✅ Ejemplo: juan@ejemplo.com
✅ Se valida automáticamente
```

### Número de Celular 📱
```
❌ Opcional (puedes dejar vacío)
✅ Formato: +56 9 XXXX XXXX
✅ Se formatea automáticamente
✅ Ejemplos aceptados:
   • 912345678
   • 56912345678
   • +56912345678
   • +56 9 1234 5678
   • +56-9-1234-5678
```

---

## ✨ Lo que pasa automáticamente

### 📱 Con el número de celular:
```
Tú escribes: "912345678"
Sistema convierte a: "+56912345678"
Se guarda como: "+56912345678"
```

### 📧 Con el correo:
```
Se valida: usuario@dominio.com
Si no cumple: Muestra error en rojo
Corrección: Intenta nuevamente
```

### 👤 Con el nombre:
```
Se valida: No puede estar vacío
Si falta: Muestra "Nombre requerido"
Corrección: Ingresa tu nombre
```

---

## 🎨 Interfaz

### Durante la edición
- ✅ Campos con bordes claros
- ✅ Etiquetas descripción bajo campos
- ✅ Errores en rojo 🔴
- ✅ Iconos Material Symbols

### Mientras guarda
- ⏳ Botón muestra "Guardando..."
- ⏳ Spinner animado
- ⏳ Espera 2 segundos

### Después de guardar
- ✅ Confirmación verde: "Perfil actualizado correctamente"
- ✅ Modal se cierra automáticamente
- ✅ Página recarga
- ✅ Cambios visibles en toda la app

---

## 🔍 Validaciones en Vivo

### Email
```
Mientras escribes:
✅ usuario@dominio.com → Verde ✓
❌ usuariodominio.com → Rojo (falta @)
❌ usuario@ → Rojo (falta dominio)
```

### Número de Celular
```
Mientras escribes:
✅ +56 9 1234 5678 → Verde ✓
✅ 912345678 → Verde ✓
❌ 9 1234 ABC → Se elimina la "ABC"
❌ 912345 @ → Se elimina la "@"
```

### Nombre
```
Mientras escribes:
✅ Juan Pérez → Verde ✓
❌ (vacío) → Error al intentar guardar
```

---

## ⌨️ Atajos de Teclado

```
ESC → Cierra el modal
ENTER → Guarda (cuando estés en el formulario)
TAB → Navega entre campos
```

---

## 💡 Tips y Trucos

### 💡 Tip 1: Celular con espacios
```
Puedes escribir: +56 9 1234 5678
Y se guarda bien con los espacios
```

### 💡 Tip 2: Cambiar solo un campo
```
No necesitas cambiar todo
Solo modifica lo que quieras
```

### 💡 Tip 3: Campo opcional
```
Si el correo o celular no lo quieres rellenar
Déjalos vacíos, no hay problema ✓
```

### 💡 Tip 4: Error? No te preocupes
```
Si hay error:
• Se muestra en rojo debajo del campo
• Puedes ver qué está mal
• Corriges y intentas de nuevo
```

---

## ❌ Errores Comunes

### Error: "El nombre es requerido"
```
❌ Problema: Dejaste el nombre vacío
✅ Solución: Ingresa tu nombre completo
```

### Error: "El correo no tiene un formato válido"
```
❌ Problema: Escribiste: "usuario-invalido.com"
✅ Solución: Debe ser: "usuario@dominio.com"
```

### Error: "El número de celular solo puede contener dígitos"
```
❌ Problema: Escribiste: "9 1234 ABC"
✅ Solución: Solo números: "912345678"
```

### Error: Cambios no se guardan
```
❌ Posible problema: Conexión de internet
✅ Solución: Verifica tu conexión e intenta de nuevo
```

---

## 🔒 Privacidad

✅ Tus datos se guardan en Supabase
✅ Solo tú puedes editarlos
✅ Se usa conexión segura (HTTPS)
✅ No se comparten datos

---

## 🆘 ¿Necesitas Ayuda?

1. **Lee las validaciones** - Tienen pistas
2. **Usa los ejemplos** - Copia el formato
3. **Revisa la documentación** - Más detalles en EDITAR_PERFIL_DOCUMENTACION.md
4. **Contacta soporte** - Si hay un problema técnico

---

## 📱 En Móvil

```
✅ Modal se adapta al tamaño
✅ Botones son más grandes
✅ Campos fáciles de escribir
✅ Todo funciona igual que en desktop
```

---

## 🌙 Dark Mode

```
✅ Interfaz se adapta automáticamente
✅ Colores claros en fondo oscuro
✅ Ojos cómodos durante la noche 😴
```

---

## 🎉 ¡Listo!

Ahora sabes cómo editar tu perfil. 

**Resumen rápido:**
1. Click en "Editar Perfil"
2. Modifica los datos
3. Click en "Guardar"
4. ✅ ¡Hecho!

---

**Última actualización**: 11 de noviembre de 2025
**Versión**: 1.0
**¿Preguntas?** Revisa la documentación completa 📚
