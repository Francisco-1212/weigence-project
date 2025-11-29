# 🚀 Guía Rápida: Sistema de Roles en Weigence

## 📋 En 2 minutos

### Los 5 Roles

| Rol | Acceso | Ver en sidebar |
|-----|--------|---|
| 💊 **Farmacéutico** | Dashboard, Inventario | Básico |
| 📦 **Bodeguera** | + Movimientos, Alertas | + Movimientos |
| 👔 **Supervisor** | + Auditoría | + Auditoría |
| 👨‍💼 **Jefe** | **TODO** + Usuarios | ⭐ Usuarios |
| 🔑 **Admin** | **TODO sin límites** | ⭐ Usuarios |

---

## 🔑 Conceptos Clave

### 1️⃣ Usuarios Jefe y Admin = Pueden crear/editar otros usuarios
### 2️⃣ Cambiar rol = El usuario ve nuevas secciones después de logout
### 3️⃣ Acceso denegado = Redirige al dashboard
### 4️⃣ APIs devuelven 403 si sin permiso

---

## 🔧 Proteger una Nueva Ruta

```python
from .decorators import requiere_rol

# Opción 1: Solo algunos roles
@bp.route('/mi-ruta')
@requiere_rol('jefe', 'administrador')
def mi_ruta():
    pass

# Opción 2: Todos excepto algunos
@bp.route('/mi-ruta')
@requiere_rol('farmaceutico', 'bodeguera', 'supervisor', 'jefe', 'administrador')
def mi_ruta():
    pass
```

---

## 🧪 Prueba Rápida

1. **Login** con diferentes usuarios
2. **Observa** el sidebar cambia
3. **Intenta** acceder a `/usuarios` sin ser Jefe/Admin
4. **Resultado** → Redirige al dashboard ✅

---

## 📂 Archivos Importantes

| Archivo | Propósito |
|---------|-----------|
| `app/config/roles_permisos.py` | Define roles, permisos y acciones |
| `app/routes/decorators.py` | Implementa @requiere_rol |
| `app/templates/componentes/sidebar.html` | Menú dinámico por rol |
| `app/templates/login.html` | Página con info de roles |
| `DOCUMENTACION_SISTEMA_ROLES.md` | Documentación completa |

---

## ❓ Preguntas Rápidas

**¿Cómo cambio el rol de un usuario?**  
→ Inicia sesión como Jefe o Admin → Sección "Usuarios" → Click en ✏️ → Cambiar rol

**¿Qué pasa si un usuario baja su permiso?**  
→ Debe hacer logout y volver a login para que se actualice

**¿Puedo dar múltiples roles a un usuario?**  
→ No, cada usuario tiene UN solo rol

**¿Cómo agrego un nuevo rol?**  
→ Edita `app/config/roles_permisos.py` y agrega configuración

**¿Qué pasa si acceso sin permisos?**  
→ Página HTML: redirige a dashboard  
→ API: devuelve HTTP 403 con error JSON

---

## ✅ Checklist Implementación

- ✅ 5 roles con permisos diferentes
- ✅ Sidebar dinámico
- ✅ Todas las rutas protegidas
- ✅ APIs protegidas
- ✅ Página login mejorada
- ✅ Documentación completa

---

## 🎯 Resumen

| Usuario | Puede | No puede |
|---------|-------|----------|
| Farmacéutico | Ver stock, registrar ventas | Crear productos, ver usuarios |
| Bodeguera | Movimientos, alertas | Ventas, usuarios |
| Supervisor | Auditoría, reportes | Crear usuarios |
| Jefe | **TODO** incluyendo usuarios | - |
| Admin | **TODO** sin límites | - |

---

**Sistema completo y funcionando. ✅**

Más detalles en: `DOCUMENTACION_SISTEMA_ROLES.md`
