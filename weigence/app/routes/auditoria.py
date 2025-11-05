from flask import render_template
from .utils import requiere_login
from . import bp  

@bp.route('/auditoria')
@requiere_login
def auditoria():
    return render_template('pagina/auditoria.html')
