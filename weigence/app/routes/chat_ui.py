from flask import Blueprint, render_template

bp = Blueprint("chat_ui", __name__, url_prefix="/chat")


@bp.route("/")
def chat_page():
    return render_template("componentes/chat.html")

