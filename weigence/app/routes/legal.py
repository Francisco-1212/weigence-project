"""
Rutas para páginas legales (Política de Privacidad, Términos y Condiciones, Política de Cookies)
"""
from flask import render_template
from . import bp


@bp.route("/politica-privacidad")
def politica_privacidad():
    """Página de Política de Privacidad"""
    return render_template("legal/politica_privacidad.html")


@bp.route("/terminos-condiciones")
def terminos_condiciones():
    """Página de Términos y Condiciones"""
    return render_template("legal/terminos_condiciones.html")


@bp.route("/politica-cookies")
def politica_cookies():
    """Página de Política de Cookies"""
    return render_template("legal/politica_cookies.html")
