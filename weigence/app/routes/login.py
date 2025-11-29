from flask import render_template, jsonify, request, session, redirect, url_for, flash
from . import bp
from api.conexion_supabase import supabase
from app.utils.email_utils import enviar_correo_recuperacion, verificar_token_valido, marcar_token_usado
from app.utils.security import verify_password
import logging

logger = logging.getLogger(__name__)

# Aplicar rate limiting a rutas sensibles
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Obtener limiter desde app
def get_limiter():
    from flask import current_app
    return current_app.extensions.get('limiter')


@bp.route("/", methods=["GET", "POST"])
def login():
    # Si el usuario ya tiene sesión activa, verificar si es válida
    if session.get("usuario_logueado"):
        # Si tiene sesión pero NO marcó "Recordarme", y es una sesión temporal,
        # NO redirigir automáticamente (dejar que decida si continuar o no)
        # Solo redirigir si marcó "Recordarme" (sesión permanente)
        if session.get("recordarme_activado"):
            print(f"[LOGIN] Usuario con sesión permanente detectado: {session.get('usuario_nombre')}")
            return redirect(url_for("main.dashboard"))
        else:
            # Sesión temporal: Mostrar login pero con credenciales precargadas (opcional)
            print(f"[LOGIN] Usuario con sesión temporal - permitir nueva sesión")
            # No redirigir, mostrar login normalmente
            pass
    
    if request.method == "POST":
        usuario_input = request.form.get("usuario")
        password_input = request.form.get("password")
        recordarme = request.form.get("remember")  # Obtener si está marcado "Recordarme"

        if not usuario_input or not password_input:
            flash("Por favor completa todos los campos", "error")
            return render_template("login.html")

        usuarios = supabase.table("usuarios").select("*").execute().data

        usuario_encontrado = next(
            (u for u in usuarios if u.get("nombre") == usuario_input 
             or u.get("correo") == usuario_input 
             or u.get("rut_usuario") == usuario_input),
            None
        )

        if usuario_encontrado:
            logger.info(f"[LOGIN] Intento de login para usuario: {usuario_encontrado.get('nombre')}")
            
            # Verificar contraseña con hash seguro
            password_hash = usuario_encontrado.get("password_hash") or usuario_encontrado.get("Contraseña")
            
            # Compatibilidad: verificar si es hash o texto plano (temporal)
            if password_hash and (password_hash.startswith('$2b$') or password_hash.startswith('$2a$')):
                # Es un hash bcrypt, verificar correctamente
                password_valida = verify_password(password_input, password_hash)
            else:
                # Contraseña en texto plano (backward compatibility)
                logger.warning(f"[LOGIN] Usuario {usuario_encontrado.get('rut_usuario')} tiene contraseña sin hash")
                password_valida = (password_hash == password_input)
            
            if password_valida:
                # Crear sesión
                session["usuario_logueado"] = True
                session["usuario_nombre"] = usuario_encontrado.get("nombre")
                session["usuario_rol"] = str(usuario_encontrado.get("rol", "")).lower()  # Convertir a minúsculas
                session["usuario_id"] = usuario_encontrado.get("rut_usuario")
                session["usuario_correo"] = usuario_encontrado.get("correo")
                session["usuario_foto_perfil"] = usuario_encontrado.get("foto_perfil_url")
                
                logger.info(f"[LOGIN] ✓ Login exitoso para: {session['usuario_nombre']} (Rol: {session['usuario_rol']})")
                
                # Registrar evento de login en auditoría
                from app.utils.eventohumano import registrar_evento_humano
                registrar_evento_humano("login", f"{session['usuario_nombre']} inició sesión")
                logger.info(f"[LOGIN] ✓ Evento de auditoría registrado para: {session['usuario_nombre']}")
                
                # Registrar usuario como conectado
                from app.utils.sesiones_activas import registrar_usuario_activo
                registrar_usuario_activo(
                    session['usuario_id'],
                    session['usuario_nombre'],
                    session['usuario_rol']
                )
                logger.info(f"[LOGIN] ✓ Usuario {session['usuario_id']} registrado como conectado")
                
                # Guardar el estado de "Recordarme"
                if recordarme == "on":
                    # SESIÓN PERMANENTE: 30 días
                    session["recordarme_activado"] = True
                    session.permanent = True
                    logger.info(f"[LOGIN] Sesión PERMANENTE (30 días) para: {usuario_input}")
                else:
                    # SESIÓN TEMPORAL: Solo mientras el navegador está abierto
                    session["recordarme_activado"] = False
                    session.permanent = False
                    logger.info(f"[LOGIN] Sesión TEMPORAL (cierre navegador) para: {usuario_input}")
                
                # Marcar como modificado para que se guarde
                session.modified = True
                
                return redirect(url_for("main.dashboard"))
            else:
                logger.warning(f"[LOGIN] ✗ Contraseña incorrecta para: {usuario_input}")
                flash("Contraseña incorrecta", "error")
        else:
            logger.warning(f"[LOGIN] ✗ Usuario no encontrado: {usuario_input}")
            flash("Usuario no encontrado", "error")

    return render_template("login.html")

@bp.route("/password-reset", methods=["POST"])
def password_reset():
    """
    Endpoint para solicitar recuperación de contraseña
    Rate limited: 5 intentos por hora
    Recibe: JSON con { "email": "usuario@example.com" }
    Responde: JSON con { "success": true/false, "message": "..." }
    """
    try:
        logger.info("[PASSWORD-RESET] 📥 Nueva solicitud de recuperación de contraseña")
        
        data = request.get_json()
        logger.info(f"[PASSWORD-RESET] Datos recibidos: {data}")
        
        email = data.get("email", "").strip() if data else None
        logger.info(f"[PASSWORD-RESET] Email procesado: {email}")
        
        if not email:
            logger.warning("[PASSWORD-RESET] ⚠️ Email vacío o no proporcionado")
            return jsonify({
                "success": False,
                "message": "El correo es requerido"
            }), 400
        
        # Buscar usuario en Supabase
        logger.info(f"[PASSWORD-RESET] 🔍 Buscando usuario en Supabase con email: {email}")
        usuarios = supabase.table("usuarios").select("*").execute().data
        logger.info(f"[PASSWORD-RESET] Total usuarios encontrados: {len(usuarios)}")
        
        usuario = next(
            (u for u in usuarios if u.get("correo") == email),
            None
        )
        
        if usuario:
            # Usuario encontrado: enviar correo
            nombre = usuario.get("nombre", "Usuario")
            logger.info(f"[PASSWORD-RESET] ✅ Usuario encontrado: {nombre} ({email})")
            logger.info(f"[PASSWORD-RESET] 📧 Intentando enviar correo de recuperación a: {email}")
            
            if enviar_correo_recuperacion(email, nombre):
                logger.info(f"[PASSWORD-RESET] ✅ Correo enviado exitosamente a: {email}")
                return jsonify({
                    "success": True,
                    "message": "Si el correo existe en nuestro sistema, recibirás un enlace para restablecer la contraseña."
                }), 200
            else:
                logger.error(f"[PASSWORD-RESET] ❌ Fallo al enviar correo a: {email}")
                # Responder con mensaje genérico por seguridad
                return jsonify({
                    "success": True,
                    "message": "Si el correo existe en nuestro sistema, recibirás un enlace para restablecer la contraseña."
                }), 200
        else:
            # Usuario no encontrado (responder con mensaje genérico por seguridad)
            logger.warning(f"[PASSWORD-RESET] ⚠️ Email no encontrado en BD: {email}")
            return jsonify({
                "success": True,
                "message": "Si el correo existe en nuestro sistema, recibirás un enlace para restablecer la contraseña."
            }), 200
            
    except Exception as e:
        logger.error(f"[PASSWORD-RESET] ❌❌❌ EXCEPCIÓN CAPTURADA: {e}")
        logger.error(f"[PASSWORD-RESET] Tipo de error: {type(e).__name__}")
        logger.error(f"[PASSWORD-RESET] Stack trace:", exc_info=True)
        return jsonify({
            "success": False,
            "message": "Error procesando la solicitud"
        }), 500

@bp.route("/reset-password", methods=["GET"])
def reset_password_page():
    """
    Página para restablecer contraseña
    Recibe: token y email por query params
    """
    return render_template("reset-password.html")

@bp.route("/api/validate-reset-token", methods=["POST"])
def validate_reset_token():
    """
    Valida si un token de recuperación es válido
    """
    try:
        logger.info("="*60)
        logger.info(f"[VALIDATE-TOKEN] ========== INICIO ==========")
        logger.info(f"[VALIDATE-TOKEN] Método: {request.method}")
        logger.info(f"[VALIDATE-TOKEN] Ruta completa: {request.path}")
        logger.info(f"[VALIDATE-TOKEN] Headers:")
        for key, value in request.headers:
            logger.info(f"  {key}: {value}")
        
        # Verificar si CSRF está exento
        from flask import g
        csrf_exempt = getattr(g, '_csrf_exempt', False)
        logger.info(f"[VALIDATE-TOKEN] CSRF exento: {csrf_exempt}")
        
        data = request.get_json()
        logger.info(f"[VALIDATE-TOKEN] Data JSON recibida: {data}")
        
        email = data.get("email") if data else None
        token = data.get("token") if data else None
        
        logger.info(f"[VALIDATE-TOKEN] Email extraído: {email}")
        logger.info(f"[VALIDATE-TOKEN] Token extraído (primeros 20 chars): {token[:20] if token else 'VACÍO'}")
        
        if not email or not token:
            logger.warning(f"[VALIDATE-TOKEN] ❌ Faltan parámetros")
            return jsonify({
                "valid": False,
                "message": "Faltan parámetros requeridos"
            }), 400
        
        # Verificar token
        logger.info(f"[VALIDATE-TOKEN] Llamando a verificar_token_valido()...")
        token_valido = verificar_token_valido(email, token)
        logger.info(f"[VALIDATE-TOKEN] Resultado verificación: {token_valido}")
        
        if token_valido:
            logger.info(f"[VALIDATE-TOKEN] ✅ Token válido para: {email}")
            return jsonify({
                "valid": True,
                "message": "Token válido"
            }), 200
        else:
            logger.warning(f"[VALIDATE-TOKEN] ❌ Token inválido para: {email}")
            return jsonify({
                "valid": False,
                "message": "El enlace ha expirado o ya fue utilizado"
            }), 200
            
    except Exception as e:
        logger.error(f"[VALIDATE-TOKEN] ❌ Exception: {str(e)}")
        import traceback
        logger.error(f"[VALIDATE-TOKEN] Traceback completo:\n{traceback.format_exc()}")
        return jsonify({
            "valid": False,
            "message": "Error al validar el token"
        }), 500

@bp.route("/api/reset-password", methods=["POST"])
def reset_password_submit():
    """
    Actualiza la contraseña del usuario
    """
    try:
        data = request.get_json()
        email = data.get("email")
        token = data.get("token")
        new_password = data.get("new_password")
        
        logger.info(f"[RESET-PASSWORD] Actualizando contraseña para: {email}")
        
        if not email or not token or not new_password:
            return jsonify({
                "success": False,
                "message": "Faltan parámetros requeridos"
            }), 400
        
        # Validar token nuevamente
        if not verificar_token_valido(email, token):
            logger.warning(f"[RESET-PASSWORD] Token inválido para: {email}")
            return jsonify({
                "success": False,
                "message": "Token inválido o expirado"
            }), 400
        
        # Hash de la nueva contraseña
        from app.utils.security import hash_password
        password_hash = hash_password(new_password)
        
        # Actualizar contraseña en Supabase
        logger.info(f"[RESET-PASSWORD] Actualizando password_hash en BD para: {email}")
        result = supabase.table("usuarios").update({
            "password_hash": password_hash
        }).eq("correo", email).execute()
        
        if result.data:
            # Marcar token como usado
            marcar_token_usado(email, token)
            logger.info(f"[RESET-PASSWORD] ✅ Contraseña actualizada exitosamente para: {email}")
            
            return jsonify({
                "success": True,
                "message": "Contraseña actualizada correctamente"
            }), 200
        else:
            logger.error(f"[RESET-PASSWORD] No se pudo actualizar la contraseña para: {email}")
            return jsonify({
                "success": False,
                "message": "No se pudo actualizar la contraseña"
            }), 500
            
    except Exception as e:
        logger.error(f"[RESET-PASSWORD] Error: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "message": "Error al actualizar la contraseña"
        }), 500

@bp.route("/logout")
def logout():
    # Registrar evento de logout antes de limpiar sesión
    from app.utils.eventohumano import registrar_evento_humano
    usuario_nombre = session.get("usuario_nombre", "Usuario desconocido")
    usuario_rut = session.get("usuario_id")
    logger.info(f"[LOGOUT] Usuario cerrando sesión: {usuario_nombre}")
    registrar_evento_humano("logout", f"{usuario_nombre} cerró sesión")
    logger.info(f"[LOGOUT] ✓ Evento de auditoría registrado para: {usuario_nombre}")
    
    # Eliminar usuario de la lista de conectados
    if usuario_rut:
        from app.utils.sesiones_activas import eliminar_usuario
        if eliminar_usuario(usuario_rut):
            logger.info(f"[LOGOUT] Usuario {usuario_rut} eliminado de usuarios conectados")
    
    session.clear()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for("main.login"))
