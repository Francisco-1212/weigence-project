# app/routes/recomendaciones.py
from flask import jsonify, request, Response
from api.conexion_supabase import supabase
from . import bp
from app.ia_engine import recomendacion_ml
import json
from app.ia_logger import registrar_ia

# -------- IA GLOBAL (header) --------
@bp.route("/api/ia/header", methods=["GET"])
def ia_header():
    recs = []
    try:
        # 1) Alertas críticas
        alertas = supabase.table("alertas").select("tipo_color").execute().data or []
        criticas = [a for a in alertas if (a.get("tipo_color") or "").lower() == "rojo"]
        if criticas:
            recs.append(f"🚨 {len(criticas)} alertas críticas activas")

        # 2) Estantes al límite
        est = supabase.table("estantes").select("peso_actual,peso_maximo").execute().data or []
        sobrecarga = [e for e in est if (e.get("peso_maximo") or 0) and (e.get("peso_actual",0)/(e["peso_maximo"])) >= 0.95]
        if sobrecarga:
            recs.append(f"⚠️ {len(sobrecarga)} estantes sobre 95% de capacidad")

        # 3) Último evento del sistema
        ev = supabase.table("eventos_sistema").select("mensaje").order("timestamp", desc=True).limit(1).execute().data or []
        if ev:
            recs.append(f"🧠 Último evento: {ev[0].get('mensaje','')}")

        if not recs:
            recs.append("✅ Sistema estable")
            ctx = request.args.get("contexto", "general")
            recs += recomendacion_ml(ctx)


        return Response(json.dumps(recs, ensure_ascii=False), mimetype="application/json; charset=utf-8")
    except Exception as e:
        print("[ia_header]", e)
        return jsonify(["⚠️ Diagnóstico no disponible"])

# -------- IA POR PANTALLA (header contextual y panel auditoría) --------
@bp.route("/api/recomendaciones", methods=["GET"])
def ia_contextual():
    ctx = (request.args.get("contexto") or "general").lower()
    recs = []

    try:
        if ctx == "dashboard":
            pend = supabase.table("alertas").select("id").eq("estado","pendiente").execute().data or []
            recs.append(f"📌 {len(pend)} alertas pendientes") if pend else recs.append("✅ Sin alertas pendientes")

        elif ctx == "inventario":
            est = supabase.table("estantes").select("id_estante,peso_actual,peso_maximo").execute().data or []
            críticos = []
            bajos = 0
            for e in est:
                mx = e.get("peso_maximo") or 0
                ac = e.get("peso_actual") or 0
                if mx <= 0: continue
                r = ac/mx
                if r >= 0.9: críticos.append(e["id_estante"])
                elif r <= 0.1: bajos += 1
            if críticos: recs.append(f"⚠️ Estantes críticos: {', '.join(map(str, críticos))}")
            if bajos: recs.append(f"ℹ️ {bajos} estantes con baja ocupación")
            if not críticos and not bajos: recs.append("✅ Niveles de carga normales")

        elif ctx == "ventas":
            ventas = supabase.table("ventas").select("total").execute().data or []
            if ventas:
                prom = sum(v.get("total",0) for v in ventas)/len(ventas)
                recs.append(f"💰 Promedio de venta: ${prom:,.0f}")
            else:
                recs.append("ℹ️ Sin ventas registradas")

        elif ctx == "movimientos":
            movs = supabase.table("movimientos_inventario") \
                           .select("tipo_evento,rut_usuario,timestamp") \
                           .order("timestamp", desc=True).execute().data or []
            entradas = sum(1 for m in movs if (m.get("tipo_evento") or "").lower() in ["entrada","añadir","agregar"])
            salidas  = sum(1 for m in movs if (m.get("tipo_evento") or "").lower() in ["salida","retirar"])
            recs.append(f"📦 {len(movs)} movimientos ({entradas} entradas / {salidas} salidas)")
            sin_usuario = sum(1 for m in movs if not m.get("rut_usuario"))
            if sin_usuario: recs.append(f"⚠️ {sin_usuario} movimientos sin usuario")

        elif ctx == "alertas":
            alertas = supabase.table("alertas") \
                               .select("titulo,tipo_color,fecha_creacion") \
                               .order("fecha_creacion", desc=True).execute().data or []
            crit = sum(1 for a in alertas if (a.get("tipo_color") or "").lower() == "rojo")
            if crit: recs.append(f"🛑 {crit} alertas críticas activas")
            if alertas: recs.append(f"📅 Última alerta: {alertas[0].get('titulo','Sin título')}")
            if not alertas and not crit: recs.append("✅ Sin alertas")

        elif ctx == "auditoria":
            # IA simple basada en heurísticas del sistema
            # 1) pesajes: dispersión
            pes = supabase.table("pesajes").select("peso_unitario").execute().data or []
            vals = [p.get("peso_unitario") for p in pes if p.get("peso_unitario") is not None]
            if len(vals) >= 5:
                avg = sum(vals)/len(vals)
                dev = max(abs(v-avg)/avg for v in vals) if avg else 0
                if dev > 0.2: recs.append("📉 Desviación alta en lecturas de peso. Revisar calibración")
                else: recs.append("✅ Lecturas de peso dentro de rangos normales")
            else:
                recs.append("ℹ️ Datos de pesajes insuficientes para diagnóstico")

            # 2) estantes críticos
            est = supabase.table("estantes").select("id_estante,peso_actual,peso_maximo").execute().data or []
            críticos = [e["id_estante"] for e in est if (e.get("peso_maximo") or 0) and (e.get("peso_actual",0)/(e["peso_maximo"])) >= 0.95]
            if críticos: recs.append(f"⚠️ Estantes >95%: {', '.join(map(str, críticos))}")

            # 3) eventos recientes
            ev = supabase.table("eventos_sistema").select("tipo,mensaje").order("timestamp", desc=True).limit(3).execute().data or []
            for e in ev:
                t = (e.get("tipo") or "").lower()
                m = e.get("mensaje","")
                if t in ["error","fallo"]: recs.append(f"🧯 Error: {m}")
                elif t in ["warning","advertencia"]: recs.append(f"⚠️ Advertencia: {m}")

            if not recs:
                recs.append("✅ Auditoría automática: sin incidencias")
            else:
                recs.append("🧠 Genera plan de acción para observaciones")

        else:
            recs.append("🧠 Sin recomendaciones para este módulo")

        return Response(json.dumps(recs, ensure_ascii=False), mimetype="application/json; charset=utf-8")
    except Exception as e:
        print("[ia_contextual]", e)
        return jsonify(["⚠️ Recomendaciones no disponibles"])
# ===========================================================
#  IA AVANZADA: interpretación del módulo de Auditoría
# ===========================================================
from app.ia_interprete import interpretar_ia_auditoria

from flask import Response
import json

@bp.route("/api/ia/auditoria", methods=["GET"])
def ia_auditoria():
    try:
        # Generar nuevo registro automático
        registrar_ia("auditoria")

        # Luego interpretar resultados
        recomendaciones = interpretar_ia_auditoria()

        # Devuelve texto con acentos y formato JSON limpio
        return Response(
            json.dumps(recomendaciones, ensure_ascii=False),
            content_type="application/json; charset=utf-8"
        )

    except Exception as e:
        print("[ia_auditoria]", e)
        return Response(
            json.dumps(["Error al generar recomendaciones automáticas."], ensure_ascii=False),
            content_type="application/json; charset=utf-8"
        )


