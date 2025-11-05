"""
Sistema de Permisos de Weigence
Define la matriz de permisos por rol
"""

PERMISOS_POR_ROL = {
    1: {  # Farmacéutico
        'nombre': 'Farmacéutico',
        'dashboard': {'ver': True},
        'inventario': {'ver': True, 'agregar': False, 'editar': False, 'eliminar': False},
        'ventas': {'ver': True, 'crear': True, 'editar': False, 'eliminar': False},
        'movimientos': {'ver': True, 'crear': False, 'editar': False},
        'alertas': {'ver': True, 'gestionar': False},
        'auditoria': {'ver': False},
        'usuarios': {'ver': False},
        'configuracion': {'ver': False}
    },
    2: {  # Bodeguero
        'nombre': 'Bodeguero',
        'dashboard': {'ver': True},
        'inventario': {'ver': True, 'agregar': True, 'editar': True, 'eliminar': False},
        'ventas': {'ver': True, 'crear': True, 'editar': False, 'eliminar': False},
        'movimientos': {'ver': True, 'crear': True, 'editar': True},
        'alertas': {'ver': True, 'gestionar': True},
        'auditoria': {'ver': False},
        'usuarios': {'ver': False},
        'configuracion': {'ver': False}
    },
    3: {  # Supervisor
        'nombre': 'Supervisor',
        'dashboard': {'ver': True},
        'inventario': {'ver': True, 'agregar': True, 'editar': True, 'eliminar': True},
        'ventas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False},
        'movimientos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False},
        'alertas': {'ver': True, 'gestionar': True},
        'auditoria': {'ver': True},
        'usuarios': {'ver': True, 'crear': False, 'editar': False},
        'configuracion': {'ver': False}
    },
    4: {  # Administrador
        'nombre': 'Administrador',
        'dashboard': {'ver': True},
        'inventario': {'ver': True, 'agregar': True, 'editar': True, 'eliminar': True},
        'ventas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
        'movimientos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
        'alertas': {'ver': True, 'gestionar': True},
        'auditoria': {'ver': True},
        'usuarios': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False},
        'configuracion': {'ver': True, 'editar': False}
    },
    5: {  # Jefe
        'nombre': 'Jefe',
        'dashboard': {'ver': True},
        'inventario': {'ver': True, 'agregar': True, 'editar': True, 'eliminar': True},
        'ventas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
        'movimientos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
        'alertas': {'ver': True, 'gestionar': True},
        'auditoria': {'ver': True},
        'usuarios': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
        'configuracion': {'ver': True, 'editar': True}
    }
}

def tiene_permiso(nivel_rol, modulo, accion):
    """
    Verifica si un rol tiene permiso para realizar una acción
    
    Args:
        nivel_rol (int): Nivel del rol (1-5)
        modulo (str): Nombre del módulo ('inventario', 'ventas', etc.)
        accion (str): Acción a verificar ('ver', 'crear', 'editar', 'eliminar')
    
    Returns:
        bool: True si tiene permiso, False si no
    """
    if nivel_rol not in PERMISOS_POR_ROL:
        return False
    
    rol_permisos = PERMISOS_POR_ROL[nivel_rol]
    
    if modulo not in rol_permisos:
        return False
    
    return rol_permisos[modulo].get(accion, False)


def obtener_permisos_usuario(nivel_rol):
    """Obtiene todos los permisos de un rol"""
    return PERMISOS_POR_ROL.get(nivel_rol, PERMISOS_POR_ROL[1])