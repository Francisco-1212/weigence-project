from flask import render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required, current_user
import re
import os
import traceback

try:
    from api.conexion_supabase import supabase
except Exception as e:
    print(f"[ERROR] Fallo al importar Supabase: {e}")
    supabase = None

from . import bp
from . import bp as main
from .decorators import puede_realizar_accion

def validar_email(email):
    """Valida que el email tenga un formato correcto"""
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None

def validar_numero_celular(numero_celular):
    """Valida que el número de celular contenga solo dígitos, espacios y caracteres válidos"""
    if not numero_celular:
        return True  # Campo opcional
    # Permite solo números, espacios, guiones, más (+) y paréntesis
    # Debe contener al menos un dígito y opcionalmente un +
    return re.match(r'^(\+?)[\d\s\-\(\)]+$', numero_celular) is not None

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
        # Asumir que es un número internacional
        return '+' + numero_celular.replace(' ', '')
    
    return numero_celular

@main.route('/editar', methods=['GET', 'POST'])
@puede_realizar_accion('perfil', 'editar')
def editar():
    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre', '').strip()
            correo = request.form.get('email', '').strip()
            numero_celular = request.form.get('numero_celular', '').strip()

            # Validaciones
            errores = []
            
            if not nombre:
                errores.append('El nombre es requerido')
            
            if correo and not validar_email(correo):
                errores.append('El correo electrónico no tiene un formato válido')
            
            if numero_celular and not validar_numero_celular(numero_celular):
                errores.append('El número de celular solo puede contener dígitos, espacios, guiones, + y paréntesis')
            
            if errores:
                for error in errores:
                    flash(error, 'danger')
                return redirect(url_for('main.editar'))

            # Formatear número de celular
            numero_celular_formateado = formatear_numero_celular(numero_celular) if numero_celular else None

            update_data = {
                "nombre": nombre,
                "correo": correo if correo else None,
                "numero celular": numero_celular_formateado
            }

            response = supabase.table("usuarios").update(update_data).eq("rut_usuario", session.get('usuario_id')).execute()

            # Verificar si hay error
            has_error = False
            if hasattr(response, 'error') and response.error:
                has_error = True
            elif not (hasattr(response, 'data') and response.data):
                has_error = True
            
            if has_error:
                flash('Error al actualizar el perfil.', 'danger')
            else:
                flash('Perfil actualizado correctamente.', 'success')
                session['usuario_nombre'] = nombre
                session['usuario_correo'] = correo if correo else session.get('usuario_correo', '')
                session['usuario_numero_celular'] = numero_celular_formateado if numero_celular_formateado else session.get('usuario_numero_celular', '')
                session.modified = True
                
                # Registrar evento de auditoría
                from app.utils.eventohumano import registrar_evento_humano
                registrar_evento_humano("editar_perfil", f"{nombre} editó su perfil")
                
            return redirect(url_for('main.editar'))
        except Exception as e:  
            flash(f'Error inesperado: {str(e)}', 'danger')
            return redirect(url_for('main.editar'))
    
    return render_template('pagina/editar.html')

@main.route('/api/test', methods=['GET'])
def api_test():
    """Endpoint de prueba simple"""
    print(f"[DEBUG] /api/test llamado")
    print(f"[DEBUG] Session keys: {list(session.keys())}")
    print(f"[DEBUG] usuario_logueado: {session.get('usuario_logueado')}")
    print(f"[DEBUG] usuario_id: {session.get('usuario_id')}")
    
    # Intentar obtener un usuario para ver qué campos tiene
    try:
        if session.get('usuario_id'):
            usuario_data = supabase.table("usuarios").select("*").eq("rut_usuario", session.get('usuario_id')).execute()
            if usuario_data.data and len(usuario_data.data) > 0:
                print(f"[DEBUG] Campos reales en Supabase: {list(usuario_data.data[0].keys())}")
                campos = list(usuario_data.data[0].keys())
            else:
                campos = []
        else:
            campos = []
    except Exception as e:
        print(f"[DEBUG] Error al obtener campos: {e}")
        campos = []
    
    return jsonify({
        'success': True, 
        'message': 'API trabajando correctamente', 
        'usuario_id': session.get('usuario_id'),
        'usuario_logueado': session.get('usuario_logueado'),
        'session_keys': list(session.keys()),
        'campos_supabase': campos
    }), 200

@main.route('/api/editar-perfil-test', methods=['POST'])
def api_editar_perfil_test():
    """Endpoint de prueba para debug"""
    try:
        print(f"[DEBUG TEST] Inicio endpoint test")
        
        if not session.get('usuario_logueado'):
            print(f"[DEBUG TEST] Usuario no autenticado")
            return jsonify({'success': False, 'error': 'No autenticado'}), 401
        
        data = request.get_json(force=True, silent=True)
        print(f"[DEBUG TEST] JSON recibido: {data}")
        
        nombre = data.get('nombre', '').strip() if data.get('nombre') else ''
        print(f"[DEBUG TEST] Nombre: {nombre}")
        
        print(f"[DEBUG TEST] Fin endpoint test - OK")
        return jsonify({'success': True, 'message': 'Test OK', 'nombre_recibido': nombre}), 200
    
    except Exception as e:
        print(f"[DEBUG TEST] Excepción: {str(e)}")
        import traceback
        print(f"[DEBUG TEST] Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500

@main.route('/api/editar-perfil', methods=['POST'])
@puede_realizar_accion('perfil', 'editar')
def api_editar_perfil_handler():
    """API endpoint para actualizar el perfil mediante AJAX"""
    
    print(f"\n{'='*60}")
    print(f"[API-EDITAR-PERFIL] INICIO - Nueva solicitud recibida")
    print(f"{'='*60}")
    
    # Verificar que el usuario está autenticado usando sesión
    if not session.get('usuario_logueado'):
        print(f"[API-EDITAR-PERFIL] ERROR: Usuario no autenticado")
        return jsonify({'success': False, 'error': 'No autenticado - Por favor inicia sesión'}), 401
    
    try:
        # Log de debug
        print(f"[API-EDITAR-PERFIL] Content-Type: {request.content_type}")
        print(f"[API-EDITAR-PERFIL] Is JSON: {request.is_json}")
        
        # Validar que el request tiene Content-Type: application/json
        if not request.is_json:
            print(f"[API-EDITAR-PERFIL] ERROR: Content-Type incorrecto")
            return jsonify({'success': False, 'error': 'Content-Type debe ser application/json'}), 400
        
        data = request.get_json(force=True, silent=True)
        print(f"[API-EDITAR-PERFIL] JSON parseado: {data}")
        
        if data is None:
            print(f"[API-EDITAR-PERFIL] ERROR: No se pudo parsear JSON")
            return jsonify({'success': False, 'error': 'No se pudo procesar el JSON'}), 400
        
        nombre = data.get('nombre', '').strip() if data.get('nombre') else ''
        correo = data.get('email', '').strip() if data.get('email') else ''
        numero_celular = data.get('numero_celular', '').strip() if data.get('numero_celular') else ''

        print(f"[API-EDITAR-PERFIL] Datos extraídos - Nombre: '{nombre}', Correo: '{correo}', Celular: '{numero_celular}'")

        # Validaciones
        if not nombre:
            print(f"[API-EDITAR-PERFIL] ERROR: Nombre vacío")
            return jsonify({'success': False, 'error': 'El nombre es requerido'}), 400
        
        if correo and not validar_email(correo):
            print(f"[API-EDITAR-PERFIL] ERROR: Email inválido: {correo}")
            return jsonify({'success': False, 'error': 'El correo electrónico no tiene un formato válido'}), 400
        
        if numero_celular and not validar_numero_celular(numero_celular):
            print(f"[API-EDITAR-PERFIL] ERROR: Número celular inválido: {numero_celular}")
            return jsonify({'success': False, 'error': 'El número de celular solo puede contener dígitos, espacios, guiones y +'}), 400

        # Obtener usuario actual de sesión
        usuario_rut = session.get('usuario_id')
        print(f"[API-EDITAR-PERFIL] Usuario RUT de sesión: {usuario_rut}")
        
        if not usuario_rut:
            print(f"[API-EDITAR-PERFIL] ERROR: Usuario RUT no encontrado en sesión")
            return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 401

        # Verificar que Supabase está disponible
        if supabase is None:
            print(f"[API-EDITAR-PERFIL] ERROR: Supabase no disponible")
            return jsonify({'success': False, 'error': 'Supabase no está disponible'}), 500

        # Formatear número de celular
        numero_celular_formateado = formatear_numero_celular(numero_celular) if numero_celular else None
        print(f"[API-EDITAR-PERFIL] Número celular formateado: '{numero_celular_formateado}'")

        update_data = {
            "nombre": nombre,
            "correo": correo if correo else None,
            "numero celular": numero_celular_formateado
        }
        
        print(f"[API-EDITAR-PERFIL] Datos a actualizar en Supabase: {update_data}")
        print(f"[API-EDITAR-PERFIL] Filtro: rut_usuario = '{usuario_rut}'")

        try:
            print(f"[API-EDITAR-PERFIL] Iniciando actualización en Supabase...")
            response = supabase.table("usuarios").update(update_data).eq("rut_usuario", usuario_rut).execute()
            print(f"[API-EDITAR-PERFIL] Supabase response recibida")
            print(f"[API-EDITAR-PERFIL] Response type: {type(response)}")
            print(f"[API-EDITAR-PERFIL] Response: {response}")
            
            # Verificar si hay atributos disponibles
            if hasattr(response, 'data'):
                print(f"[API-EDITAR-PERFIL] Response data: {response.data}")
            if hasattr(response, 'error'):
                print(f"[API-EDITAR-PERFIL] Response error: {response.error}")
                
        except Exception as e:
            print(f"[API-EDITAR-PERFIL] EXCEPTION en Supabase: {str(e)}")
            import traceback
            print(f"[API-EDITAR-PERFIL] Traceback: {traceback.format_exc()}")
            return jsonify({'success': False, 'error': f'Error en Supabase: {str(e)}'}), 500

        # Verificar si la actualización fue exitosa
        try:
            # Intentar acceder a response.data
            if hasattr(response, 'data') and response.data:
                print(f"[API-EDITAR-PERFIL] Update exitoso - Registros actualizados: {len(response.data)}")
            else:
                print(f"[API-EDITAR-PERFIL] Update completado pero sin datos en response")
        except Exception as e:
            print(f"[API-EDITAR-PERFIL] Error al verificar response: {str(e)}")
            return jsonify({'success': False, 'error': f'Error al verificar respuesta: {str(e)}'}), 500

        # Actualizar sesión
        print(f"[API-EDITAR-PERFIL] Actualizando sesión...")
        session['usuario_nombre'] = nombre
        session['usuario_correo'] = correo if correo else session.get('usuario_correo', '')
        session['usuario_numero_celular'] = numero_celular_formateado if numero_celular_formateado else session.get('usuario_numero_celular', '')
        session.modified = True

        print(f"[API-EDITAR-PERFIL] ✅ Actualización exitosa - Sesión actualizada")
        print(f"{'='*60}\n")

        return jsonify({
            'success': True,
            'message': 'Perfil actualizado correctamente',
            'usuario': {
                'nombre': nombre,
                'correo': correo,
                'numero_celular': numero_celular_formateado
            }
        }), 200

    except Exception as e:
        import traceback
        print(f"[API-EDITAR-PERFIL] ❌ EXCEPTION: {str(e)}")
        print(f"[API-EDITAR-PERFIL] Traceback completo:")
        print(traceback.format_exc())
        print(f"{'='*60}\n")
        return jsonify({'success': False, 'error': f'Error inesperado: {str(e)}'}), 500