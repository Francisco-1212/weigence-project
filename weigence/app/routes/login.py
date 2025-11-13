from flask import render_template, jsonify, request, session, redirect, url_for, flash
from . import bp
from api.conexion_supabase import supabase
from app.email_utils import enviar_correo_recuperacion, verificar_token_valido, marcar_token_usado


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
            # DEBUG: Mostrar qué usuario se encontró
            print(f"[LOGIN DEBUG] Usuario encontrado:")
            print(f"  - Nombre: {usuario_encontrado.get('nombre')}")
            print(f"  - Rol en BD: {usuario_encontrado.get('rol')}")
            print(f"  - Rol minúsculas: {str(usuario_encontrado.get('rol', '')).lower()}")
            
            if usuario_encontrado.get("Contraseña") == password_input:
                # Crear sesión
                session["usuario_logueado"] = True
                session["usuario_nombre"] = usuario_encontrado.get("nombre")
                session["usuario_rol"] = str(usuario_encontrado.get("rol", "")).lower()  # Convertir a minúsculas
                session["usuario_id"] = usuario_encontrado.get("rut_usuario")
                session["usuario_correo"] = usuario_encontrado.get("correo")
                
                # DEBUG: Mostrar sesión creada
                print(f"[LOGIN DEBUG] Sesión creada:")
                print(f"  - usuario_nombre: {session['usuario_nombre']}")
                print(f"  - usuario_rol: {session['usuario_rol']}")
                print(f"  - usuario_id: {session['usuario_id']}")
                
                # Guardar el estado de "Recordarme"
                if recordarme == "on":
                    # SESIÓN PERMANENTE: 30 días
                    session["recordarme_activado"] = True
                    session.permanent = True
                    print(f"[LOGIN] ✓ Sesión PERMANENTE (30 días) para: {usuario_input}")
                else:
                    # SESIÓN TEMPORAL: Solo mientras el navegador está abierto
                    session["recordarme_activado"] = False
                    session.permanent = False
                    print(f"[LOGIN] ✓ Sesión TEMPORAL (cierre navegador) para: {usuario_input}")
                
                # Marcar como modificado para que se guarde
                session.modified = True
                
                return redirect(url_for("main.dashboard"))
            else:
                flash("Contraseña incorrecta", "error")
        else:
            flash("Usuario no encontrado", "error")

    return render_template("login.html")

@bp.route("/password-reset", methods=["POST"])
def password_reset():
    """
    Endpoint para solicitar recuperación de contraseña
    Recibe: JSON con { "email": "usuario@example.com" }
    Responde: JSON con { "success": true/false, "message": "..." }
    """
    try:
        data = request.get_json()
        email = data.get("email", "").strip() if data else None
        
        if not email:
            return jsonify({
                "success": False,
                "message": "El correo es requerido"
            }), 400
        
        # Buscar usuario en Supabase
        usuarios = supabase.table("usuarios").select("*").execute().data
        usuario = next(
            (u for u in usuarios if u.get("correo") == email),
            None
        )
        
        if usuario:
            # Usuario encontrado: enviar correo
            nombre = usuario.get("nombre", "Usuario")
            print(f"[PASSWORD-RESET] Enviando correo de recuperación a: {email}")
            
            if enviar_correo_recuperacion(email, nombre):
                return jsonify({
                    "success": True,
                    "message": "Si el correo existe en nuestro sistema, recibirás un enlace para restablecer la contraseña."
                }), 200
            else:
                print(f"[PASSWORD-RESET] Fallo al enviar correo a: {email}")
                # Responder con mensaje genérico por seguridad
                return jsonify({
                    "success": True,
                    "message": "Si el correo existe en nuestro sistema, recibirás un enlace para restablecer la contraseña."
                }), 200
        else:
            # Usuario no encontrado (responder con mensaje genérico por seguridad)
            print(f"[PASSWORD-RESET] Email no encontrado: {email}")
            return jsonify({
                "success": True,
                "message": "Si el correo existe en nuestro sistema, recibirás un enlace para restablecer la contraseña."
            }), 200
            
    except Exception as e:
        print(f"[PASSWORD-RESET] Error: {e}")
        return jsonify({
            "success": False,
            "message": "Error procesando la solicitud"
        }), 500

@bp.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for("main.login"))
