from flask import render_template
from .utils import requiere_login
from . import bp
from .decorators import requiere_rol

@bp.route('/auditoria')
@requiere_rol('supervisor', 'jefe', 'administrador')
def auditoria():
    return render_template('pagina/auditoria.html')
