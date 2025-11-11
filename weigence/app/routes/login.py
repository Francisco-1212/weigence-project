from flask import render_template, jsonify, request, session, redirect, url_for, flash
from . import bp
from api.conexion_supabase import supabase


@bp.route("/", methods=["GET", "POST"])
def login():
    # Si el usuario ya tiene sesión activa, redirige al dashboard
    if session.get("usuario_logueado"):
        return redirect(url_for("main.dashboard"))
    
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
            if usuario_encontrado.get("Contraseña") == password_input:
                # Crear sesión
                session["usuario_logueado"] = True
                session["usuario_nombre"] = usuario_encontrado.get("nombre")
                session["usuario_rol"] = usuario_encontrado.get("rol")
                session["usuario_id"] = usuario_encontrado.get("rut_usuario")
                session["usuario_correo"] = usuario_encontrado.get("correo")
                
                # Si "Recordarme" está marcado, hacer la sesión permanente (30 días)
                if recordarme == "on":
                    session.permanent = True
                    from datetime import timedelta
                    session.permanent_session_lifetime = timedelta(days=30)
                
                return redirect(url_for("main.dashboard"))
            else:
                flash("Contraseña incorrecta", "error")
        else:
            flash("Usuario no encontrado", "error")

    return render_template("login.html")

@bp.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for("main.login"))
