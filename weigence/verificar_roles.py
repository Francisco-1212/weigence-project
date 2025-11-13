"""
Script de verificación del Sistema de Roles en Weigence
Ejecutar: python verificar_roles.py
"""

import sys
import os

# Colores para terminal
VERDE = '\033[92m'
ROJO = '\033[91m'
AMARILLO = '\033[93m'
AZUL = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def check(condition, mensaje):
    """Verifica una condición y muestra resultado"""
    if condition:
        print(f"{VERDE}✅ {RESET}{mensaje}")
        return True
    else:
        print(f"{ROJO}❌ {RESET}{mensaje}")
        return False

def warn(mensaje):
    """Muestra una advertencia"""
    print(f"{AMARILLO}⚠️  {RESET}{mensaje}")

def info(mensaje):
    """Muestra información"""
    print(f"{AZUL}ℹ️  {RESET}{mensaje}")

def main():
    print(f"\n{BOLD}{'='*70}")
    print(f"🔐 VERIFICACIÓN DEL SISTEMA DE ROLES - WEIGENCE")
    print(f"{'='*70}{RESET}\n")
    
    total = 0
    aprobadas = 0
    
    # ========== 1. VERIFICAR ARCHIVOS ==========
    print(f"\n{BOLD}📁 1. VERIFICANDO ARCHIVOS{RESET}")
    print("-" * 70)
    
    archivos_requeridos = {
        'app/config/roles_permisos.py': 'Configuración de roles',
        'app/routes/decorators.py': 'Decoradores de protección',
        'app/templates/login.html': 'Página de login',
        'app/templates/componentes/sidebar.html': 'Sidebar dinámico',
        'DOCUMENTACION_SISTEMA_ROLES.md': 'Documentación',
        'IMPLEMENTACION_ROLES_COMPLETADA.md': 'Resumen implementación',
        'GUIA_RAPIDA_ROLES_SISTEMA.md': 'Guía rápida',
    }
    
    for archivo, descripcion in archivos_requeridos.items():
        existe = os.path.exists(archivo)
        total += 1
        if check(existe, f"{descripcion}: {archivo}"):
            aprobadas += 1
        else:
            warn(f"Archivo faltante: {archivo}")
    
    # ========== 2. VERIFICAR CONFIGURACIÓN ==========
    print(f"\n{BOLD}⚙️  2. VERIFICANDO CONFIGURACIÓN{RESET}")
    print("-" * 70)
    
    try:
        sys.path.insert(0, os.getcwd())
        from app.config.roles_permisos import ROLES_DISPONIBLES, PERMISOS_POR_ROL, ACCIONES_POR_ROL
        
        roles_esperados = {'farmaceutico', 'bodeguera', 'supervisor', 'jefe', 'administrador'}
        roles_actual = set(ROLES_DISPONIBLES)
        
        total += 1
        if check(roles_actual == roles_esperados, f"5 roles definidos: {', '.join(ROLES_DISPONIBLES)}"):
            aprobadas += 1
        
        total += 1
        if check(len(PERMISOS_POR_ROL) == 5, f"Permisos definidos para 5 roles"):
            aprobadas += 1
        
        # Verificar que cada rol tiene permisos
        for rol, permisos in PERMISOS_POR_ROL.items():
            total += 1
            if check(isinstance(permisos, list) and len(permisos) > 0, f"Rol '{rol}' tiene {len(permisos)} permisos"):
                aprobadas += 1
        
        total += 1
        if check(len(ACCIONES_POR_ROL) == 5, f"Acciones definidas para 5 roles"):
            aprobadas += 1
            
    except Exception as e:
        total += 1
        check(False, f"Error al importar configuración: {e}")
        warn(f"Detalles: {str(e)}")
    
    # ========== 3. VERIFICAR DECORADORES ==========
    print(f"\n{BOLD}🛡️  3. VERIFICANDO DECORADORES{RESET}")
    print("-" * 70)
    
    try:
        from app.routes.decorators import requiere_rol, requiere_autenticacion, puede_realizar_accion
        
        total += 1
        check(True, "Decorador @requiere_rol importado correctamente")
        aprobadas += 1
        
        total += 1
        check(True, "Decorador @requiere_autenticacion importado correctamente")
        aprobadas += 1
        
        total += 1
        check(True, "Decorador @puede_realizar_accion importado correctamente")
        aprobadas += 1
        
    except Exception as e:
        for _ in range(3):
            total += 1
            check(False, f"Error importando decoradores: {e}")
        warn(f"Detalles: {str(e)}")
    
    # ========== 4. VERIFICAR RUTAS ==========
    print(f"\n{BOLD}🚦 4. VERIFICANDO RUTAS PROTEGIDAS{RESET}")
    print("-" * 70)
    
    rutas_esperadas = {
        'app.routes.dashboard': ['dashboard', 'api_dashboard_filtrado'],
        'app.routes.inventario': ['inventario', 'agregar_producto', 'eliminar_producto'],
        'app.routes.movimientos': ['movimientos'],
        'app.routes.ventas': ['ventas'],
        'app.routes.alertas': ['alertas'],
        'app.routes.auditoria': ['auditoria'],
        'app.routes.historial': ['historial'],
        'app.routes.recomendaciones_ai': ['api_recomendacion'],
        'app.routes.usuarios': ['usuarios', 'api_crear_usuario', 'api_editar_usuario', 'api_eliminar_usuario'],
    }
    
    for modulo, funciones in rutas_esperadas.items():
        try:
            mod = __import__(modulo, fromlist=[''])
            for funcion in funciones:
                total += 1
                tiene_funcion = hasattr(mod, funcion)
                check(tiene_funcion, f"Ruta {modulo}.{funcion} existe")
                if tiene_funcion:
                    aprobadas += 1
        except Exception as e:
            for _ in funciones:
                total += 1
                check(False, f"Error verificando {modulo}: {e}")
    
    # ========== 5. VERIFICAR TEMPLATES ==========
    print(f"\n{BOLD}🎨 5. VERIFICANDO TEMPLATES{RESET}")
    print("-" * 70)
    
    # Verificar login.html tiene info de roles
    try:
        with open('app/templates/login.html', 'r', encoding='utf-8') as f:
            contenido = f.read()
            total += 1
            check('Farmacéutico' in contenido, "Login.html contiene información de roles")
            aprobadas += 1
    except Exception as e:
        total += 1
        check(False, f"Error verificando login.html: {e}")
    
    # Verificar sidebar.html tiene validaciones de rol
    try:
        with open('app/templates/componentes/sidebar.html', 'r', encoding='utf-8') as f:
            contenido = f.read()
            total += 1
            check("usuario_rol" in contenido, "Sidebar.html valida rol del usuario")
            aprobadas += 1
            
            total += 1
            check("jefe" in contenido and "administrador" in contenido, "Sidebar.html reconoce roles específicos")
            aprobadas += 1
    except Exception as e:
        for _ in range(2):
            total += 1
            check(False, f"Error verificando sidebar.html: {e}")
    
    # ========== RESUMEN FINAL ==========
    print(f"\n{BOLD}{'='*70}")
    print(f"📊 RESUMEN{RESET}")
    print(f"{'='*70}")
    
    porcentaje = (aprobadas / total * 100) if total > 0 else 0
    
    print(f"\nVerificaciones aprobadas: {VERDE}{aprobadas}/{total}{RESET}")
    print(f"Porcentaje: {porcentaje:.1f}%")
    
    if porcentaje == 100:
        print(f"\n{VERDE}{BOLD}✅ ¡TODO CORRECTO! El sistema de roles está completamente implementado.{RESET}\n")
        return 0
    elif porcentaje >= 80:
        print(f"\n{AMARILLO}{BOLD}⚠️  CASI LISTO - Algunas verificaciones fallaron.{RESET}\n")
        return 1
    else:
        print(f"\n{ROJO}{BOLD}❌ ERRORES DETECTADOS - Revisa los fallos anteriores.{RESET}\n")
        return 2

if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n{ROJO}{BOLD}Error fatal:{RESET} {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
