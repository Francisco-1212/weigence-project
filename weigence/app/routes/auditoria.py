from flask import render_template
from . import bp  

@bp.route('/auditoria')
def auditoria():
    return render_template('pagina/auditoria.html')
