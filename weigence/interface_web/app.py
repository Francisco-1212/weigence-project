from flask import Flask, render_template, jsonify
from sys import path
path.append(r"e:\Github\weigence-project\weigence")
from conexion_bd.conexion_supabase import supabase

app = Flask(__name__)

@app.route("/")
def dashboard():
    productos = supabase.table("productos").select("*").execute().data
    pesajes = supabase.table("pesajes").select("*").execute().data
    usuarios = supabase.table("usuarios").select("*").execute().data
    estantes = supabase.table("estantes").select("*").execute().data
    historial = supabase.table("historial").select("*").execute().data

    return render_template(
        "index.html",
        productos=productos,
        pesajes=pesajes,
        usuarios=usuarios,
        estantes=estantes,
        historial=historial
    )

if __name__ == "__main__":
    app.run(debug=True)