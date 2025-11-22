"""
Sistema de rastreo de usuarios conectados en tiempo real
Módulo centralizado para compartir estado entre diferentes rutas
"""
from datetime import datetime
from threading import Lock

# Diccionario thread-safe para usuarios activos
# Formato: {rut_usuario: {'nombre': str, 'rol': str, 'ultima_actividad': datetime}}
_usuarios_activos = {}
_lock = Lock()


def registrar_usuario_activo(rut, nombre, rol):
    """Registra un usuario como activo"""
    with _lock:
        _usuarios_activos[rut] = {
            'nombre': nombre,
            'rol': rol,
            'ultima_actividad': datetime.now()
        }
        print(f"[SESIONES] ✓ Usuario registrado: {nombre} ({rut}) - Total: {len(_usuarios_activos)}")


def actualizar_heartbeat(rut, nombre, rol):
    """Actualiza el timestamp de actividad de un usuario"""
    with _lock:
        ahora = datetime.now()
        era_nuevo = rut not in _usuarios_activos
        
        _usuarios_activos[rut] = {
            'nombre': nombre,
            'rol': rol,
            'ultima_actividad': ahora
        }
        
        if era_nuevo:
            print(f"[SESIONES] 🆕 Usuario nuevo conectado: {nombre} ({rut}) - Total: {len(_usuarios_activos)}")
        else:
            print(f"[SESIONES] ✓ Heartbeat actualizado: {nombre} ({rut}) a las {ahora.strftime('%H:%M:%S')} - Total: {len(_usuarios_activos)}")
        
        # Mostrar todos los usuarios activos
        print(f"[SESIONES] 📋 Usuarios activos: {list(_usuarios_activos.keys())}")


def eliminar_usuario(rut):
    """Elimina un usuario de la lista de activos"""
    with _lock:
        if rut in _usuarios_activos:
            nombre = _usuarios_activos[rut].get('nombre', rut)
            del _usuarios_activos[rut]
            print(f"[SESIONES] ✓ Usuario eliminado: {nombre} ({rut}) - Total: {len(_usuarios_activos)}")
            return True
        return False


def obtener_usuarios_conectados(timeout_minutos=2):
    """
    Obtiene la lista de usuarios conectados, limpiando los inactivos
    
    Args:
        timeout_minutos: Minutos de inactividad antes de considerar desconectado
        
    Returns:
        tuple: (lista de RUTs conectados, diccionario con detalles)
    """
    from datetime import timedelta
    
    with _lock:
        ahora = datetime.now()
        usuarios_a_eliminar = []
        
        # Identificar usuarios inactivos
        for rut, info in _usuarios_activos.items():
            if 'ultima_actividad' in info:
                tiempo_inactivo = ahora - info['ultima_actividad']
                if tiempo_inactivo > timedelta(minutes=timeout_minutos):
                    usuarios_a_eliminar.append(rut)
                    print(f"[SESIONES] ⚠️ Usuario inactivo detectado: {info.get('nombre')} ({rut}) - Última actividad: {info['ultima_actividad']}")
        
        # Eliminar usuarios inactivos
        for rut in usuarios_a_eliminar:
            nombre = _usuarios_activos[rut].get('nombre', rut)
            del _usuarios_activos[rut]
            print(f"[SESIONES] ✗ Usuario marcado como desconectado: {nombre} ({rut})")
        
        # Devolver copia de los datos
        usuarios_ruts = list(_usuarios_activos.keys())
        detalles = {
            rut: {
                'nombre': info.get('nombre'),
                'rol': info.get('rol'),
                'ultima_actividad': info.get('ultima_actividad').isoformat() if info.get('ultima_actividad') else None
            }
            for rut, info in _usuarios_activos.items()
        }
        
        print(f"[SESIONES] 📊 Total usuarios conectados: {len(usuarios_ruts)} - RUTs: {usuarios_ruts}")
        
        return usuarios_ruts, detalles


def obtener_total_conectados():
    """Obtiene el número total de usuarios conectados"""
    with _lock:
        return len(_usuarios_activos)


def limpiar_todo():
    """Limpia todos los usuarios (útil para debugging)"""
    with _lock:
        _usuarios_activos.clear()
        print("[SESIONES] ✓ Todos los usuarios han sido limpiados")
