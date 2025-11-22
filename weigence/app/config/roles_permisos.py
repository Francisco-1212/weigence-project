"""
Configuración centralizada de roles y permisos en Weigence
Archivo: app/config/roles_permisos.py
"""

# ============================================================================
# 🔐 ROLES DISPONIBLES EN EL SISTEMA
# ============================================================================

ROLES_DISPONIBLES = [
    'operador',
    'supervisor',
    'administrador'
]

# ============================================================================
# 📊 DESCRIPCIÓN DE CADA ROL
# ============================================================================

DESCRIPCION_ROLES = {
    'operador': {
        'nombre_completo': 'Operador',
        'descripcion': 'Personal operativo. Acceso a dashboard, inventario, movimientos, ventas y alertas.',
        'color': 'blue',
        'icono': '👤'
    },
    'supervisor': {
        'nombre_completo': 'Supervisor',
        'descripcion': 'Supervisión completa. Acceso total a todas las funcionalidades del sistema.',
        'color': 'yellow',
        'icono': '👔'
    },
    'administrador': {
        'nombre_completo': 'Administrador',
        'descripcion': 'Control total del sistema y todas las funcionalidades.',
        'color': 'purple',
        'icono': '🔑'
    }
}

# ============================================================================
# 🎯 PERMISOS POR ROL - DEFINE ACCESO A SECCIONES DEL SISTEMA
# ============================================================================

PERMISOS_POR_ROL = {
    'operador': [
        'dashboard',
        'inventario',
        'movimientos',
        'ventas',
        'alertas',
        'perfil'
    ],
    'supervisor': [
        'dashboard',
        'inventario',
        'movimientos',
        'alertas',
        'auditoria',
        'ventas',
        'usuarios',
        'historial',
        'recomendaciones',
        'perfil'
    ],
    'administrador': [
        'dashboard',
        'inventario',
        'movimientos',
        'alertas',
        'auditoria',
        'ventas',
        'usuarios',
        'historial',
        'recomendaciones',
        'perfil'
    ]
}

# ============================================================================
# 🔓 RUTAS PÚBLICAS - NO REQUIEREN AUTENTICACIÓN
# ============================================================================

RUTAS_PUBLICAS = [
    'main.login',
    'main.logout',
    'main.password_reset',
    'main.reset_password_with_token'
]

# ============================================================================
# 🛡️ RUTAS PROTEGIDAS - REQUIEREN ROLES ESPECÍFICOS
# ============================================================================

RUTAS_PROTEGIDAS = {
    # Dashboard - Todos los usuarios autenticados
    'main.dashboard': ['operador', 'supervisor', 'administrador'],
    
    # Inventario - Todos
    'main.inventario': ['operador', 'supervisor', 'administrador'],
    
    # Movimientos - Todos
    'main.movimientos': ['operador', 'supervisor', 'administrador'],
    
    # Ventas - Todos
    'main.ventas': ['operador', 'supervisor', 'administrador'],
    
    # Alertas - Todos
    'main.alertas': ['operador', 'supervisor', 'administrador'],
    
    # Auditoría - Solo Supervisor y Admin
    'main.auditoria': ['supervisor', 'administrador'],
    
    # Usuarios (CRUD) - Solo Supervisor y Admin
    'main.usuarios': ['supervisor', 'administrador'],
    
    # Historial - Solo Supervisor y Admin
    'main.historial': ['supervisor', 'administrador'],
    
    # Recomendaciones IA - Solo Supervisor y Admin
    'main.recomendaciones_ai': ['supervisor', 'administrador'],
    
    # Perfil - Todos
    'main.perfil': ['operador', 'supervisor', 'administrador'],
}

# ============================================================================
# 📋 MATRIZ DE ACCIONES POR ROL
# ============================================================================

ACCIONES_POR_ROL = {
    'operador': {
        'inventario': {
            'ver': True,
            'crear': True,
            'editar': True,
            'eliminar': False,
            'ver_vencimientos': True,
            'ver_stock': True,
            'registrar_ventas': True
        },
        'movimientos': {
            'ver': True,
            'crear': True,
            'editar': True,
            'eliminar': False
        },
        'ventas': {
            'ver': True,
            'crear': True,
            'editar': True,
            'eliminar': False,
            'ver_reportes': True,
            'exportar': False
        },
        'alertas': {
            'ver': True,
            'crear': False,
            'editar': False,
            'eliminar': False
        },
        'usuarios': {
            'ver': False,
            'crear': False,
            'editar': False,
            'eliminar': False
        },
        'perfil': {
            'ver': True,
            'editar': True
        }
    },
    
    'supervisor': {
        'inventario': {
            'ver': True,
            'crear': True,
            'editar': True,
            'eliminar': True,
            'ver_vencimientos': True,
            'ver_stock': True,
            'registrar_ventas': True
        },
        'movimientos': {
            'ver': True,
            'crear': True,
            'editar': True,
            'eliminar': True
        },
        'ventas': {
            'ver': True,
            'crear': True,
            'editar': True,
            'eliminar': True,
            'ver_reportes': True,
            'exportar': True
        },
        'auditoria': {
            'ver': True,
            'descargar': True,
            'exportar': True
        },
        'usuarios': {
            'ver': True,
            'crear': True,
            'editar': True,
            'eliminar': True,
            'asignar_rol': True
        },
        'historial': {
            'ver': True,
            'descargar': True,
            'exportar': True
        },
        'recomendaciones': {
            'ver': True,
            'configurar': True
        },
        'perfil': {
            'ver': True,
            'editar': True
        }
    },
    
    'administrador': {
        'inventario': {
            'ver': True,
            'crear': True,
            'editar': True,
            'eliminar': True,
            'ver_vencimientos': True,
            'ver_stock': True,
            'registrar_ventas': True
        },
        'movimientos': {
            'ver': True,
            'crear': True,
            'editar': True,
            'eliminar': True
        },
        'ventas': {
            'ver': True,
            'crear': True,
            'editar': True,
            'eliminar': True,
            'ver_reportes': True,
            'exportar': True
        },
        'auditoria': {
            'ver': True,
            'descargar': True,
            'exportar': True
        },
        'usuarios': {
            'ver': True,
            'crear': True,
            'editar': True,
            'eliminar': True,
            'asignar_rol': True
        },
        'historial': {
            'ver': True,
            'descargar': True,
            'exportar': True
        },
        'recomendaciones': {
            'ver': True,
            'configurar': True
        },
        'perfil': {
            'ver': True,
            'editar': True
        }
    }
}

# ============================================================================
# 🚀 FUNCIONES AUXILIARES
# ============================================================================

def obtener_permisos_rol(rol):
    """
    Obtiene la lista de permisos para un rol específico
    
    Args:
        rol (str): El rol del usuario
        
    Returns:
        list: Lista de secciones permitidas para ese rol
    """
    return PERMISOS_POR_ROL.get(rol, [])


def usuario_puede_acceder(rol, seccion):
    """
    Verifica si un usuario con cierto rol puede acceder a una sección
    
    Args:
        rol (str): El rol del usuario
        seccion (str): La sección a la que intenta acceder
        
    Returns:
        bool: True si tiene acceso, False en caso contrario
    """
    permisos = PERMISOS_POR_ROL.get(rol, [])
    return seccion in permisos


def usuario_puede_realizar_accion(rol, seccion, accion):
    """
    Verifica si un usuario puede realizar una acción específica
    
    Args:
        rol (str): El rol del usuario
        seccion (str): La sección del sistema
        accion (str): La acción a realizar (crear, editar, eliminar, etc)
        
    Returns:
        bool: True si puede realizar la acción, False en caso contrario
    """
    acciones = ACCIONES_POR_ROL.get(rol, {})
    seccion_acciones = acciones.get(seccion, {})
    return seccion_acciones.get(accion, False)


def obtener_descripcion_rol(rol):
    """
    Obtiene la descripción completa de un rol
    
    Args:
        rol (str): El rol
        
    Returns:
        dict: Diccionario con información del rol
    """
    return DESCRIPCION_ROLES.get(rol, {
        'nombre_completo': rol.capitalize(),
        'descripcion': 'Rol personalizado',
        'color': 'gray',
        'icono': '👤'
    })
