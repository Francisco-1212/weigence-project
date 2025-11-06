from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from api.conexion_supabase import supabase
from . import bp
from . import bp as main

@main.route('/editar', methods=['GET', 'POST'])
@login_required
def editar():
    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre')
            email = request.form.get('email')
            telefono = request.form.get('telefono')

            update_data = {
                "nombre": nombre,
                "email": email,
                "telefono": telefono
            }

            response = supabase.table("usuarios").update(update_data).eq("rut_usuario", current_user.rut_usuario).execute()

            if response.error:
                flash('Error al actualizar el perfil.', 'danger')
            else:
                flash('Perfil actualizado correctamente.', 'success')
                session['usuario_logueado']['nombre'] = nombre
                session['usuario_logueado']['email'] = email
                session['usuario_logueado']['telefono'] = telefono
            return redirect(url_for('main.editar'))
        except Exception as e:  
            flash(f'Error inesperado: {str(e)}', 'danger')
            return redirect(url_for('main.editar'))
    
    return render_template('pagina/editar.html')