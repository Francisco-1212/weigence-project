"""
Utilidades de seguridad para hash de contraseñas y validación
"""
import bcrypt
import re
from typing import Optional


def hash_password(password: str) -> str:
    """
    Genera un hash seguro de la contraseña usando bcrypt
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        str: Hash de la contraseña
    """
    if not password:
        raise ValueError("La contraseña no puede estar vacía")
    
    # Generar salt y hash
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash
    
    Args:
        password: Contraseña en texto plano
        hashed: Hash almacenado
        
    Returns:
        bool: True si coincide, False si no
    """
    if not password or not hashed:
        return False
    
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception as e:
        print(f"[SECURITY] Error verificando contraseña: {e}")
        return False


def validar_fortaleza_password(password: str) -> tuple[bool, Optional[str]]:
    """
    Valida que la contraseña cumpla requisitos mínimos de seguridad
    
    Requisitos:
    - Mínimo 8 caracteres
    - Al menos una mayúscula
    - Al menos una minúscula
    - Al menos un número
    
    Args:
        password: Contraseña a validar
        
    Returns:
        tuple: (es_valida, mensaje_error)
    """
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    
    if not re.search(r'[A-Z]', password):
        return False, "La contraseña debe contener al menos una mayúscula"
    
    if not re.search(r'[a-z]', password):
        return False, "La contraseña debe contener al menos una minúscula"
    
    if not re.search(r'\d', password):
        return False, "La contraseña debe contener al menos un número"
    
    return True, None


def sanitizar_input(texto: str, max_length: int = 200) -> str:
    """
    Sanitiza entrada de usuario eliminando caracteres peligrosos
    
    Args:
        texto: Texto a sanitizar
        max_length: Longitud máxima permitida
        
    Returns:
        str: Texto sanitizado
    """
    if not texto:
        return ""
    
    # Limitar longitud
    texto = texto[:max_length]
    
    # Eliminar caracteres de control y scripts
    texto = re.sub(r'[<>"\']', '', texto)
    
    # Eliminar espacios múltiples
    texto = re.sub(r'\s+', ' ', texto)
    
    return texto.strip()


def validar_email(email: str) -> bool:
    """
    Valida formato de email
    
    Args:
        email: Email a validar
        
    Returns:
        bool: True si es válido
    """
    if not email:
        return False
    
    # Patrón básico de email
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(patron, email))


def validar_rut_chileno(rut: str) -> bool:
    """
    Valida formato de RUT chileno (XX.XXX.XXX-X o XXXXXXXX-X)
    
    Args:
        rut: RUT a validar
        
    Returns:
        bool: True si es válido
    """
    if not rut:
        return False
    
    # Remover puntos y guiones
    rut_limpio = rut.replace('.', '').replace('-', '')
    
    # Debe tener entre 8 y 9 caracteres
    if len(rut_limpio) < 8 or len(rut_limpio) > 9:
        return False
    
    # Separar cuerpo y dígito verificador
    cuerpo = rut_limpio[:-1]
    dv = rut_limpio[-1].upper()
    
    # Verificar que el cuerpo sea numérico
    if not cuerpo.isdigit():
        return False
    
    # Calcular dígito verificador
    suma = 0
    multiplicador = 2
    
    for digito in reversed(cuerpo):
        suma += int(digito) * multiplicador
        multiplicador += 1
        if multiplicador > 7:
            multiplicador = 2
    
    resto = suma % 11
    dv_calculado = 11 - resto
    
    if dv_calculado == 11:
        dv_esperado = '0'
    elif dv_calculado == 10:
        dv_esperado = 'K'
    else:
        dv_esperado = str(dv_calculado)
    
    return dv == dv_esperado
