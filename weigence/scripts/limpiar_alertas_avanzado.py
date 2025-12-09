"""
Script para limpiar alertas resueltas/descartadas antiguas y spam de alertas
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.conexion_supabase import supabase
from datetime import datetime, timedelta

def limpiar_alertas_resueltas_antiguas(dias=7, confirmar=False):
    """Elimina alertas resueltas/descartadas con más de X días"""
    if not confirmar:
        print(f"\n⚠️  Esta función eliminará alertas resueltas/descartadas con más de {dias} días")
        print("Para confirmar, ejecuta con --confirmar")
        return
    
    fecha_limite = (datetime.now() - timedelta(days=dias)).isoformat()
    
    # Contar
    resueltas = supabase.table("alertas")\
        .select("id", count="exact")\
        .eq("estado", "resuelto")\
        .lt("fecha_creacion", fecha_limite)\
        .execute()
    
    descartadas = supabase.table("alertas")\
        .select("id", count="exact")\
        .eq("estado", "descartada")\
        .lt("fecha_creacion", fecha_limite)\
        .execute()
    
    total = resueltas.count + descartadas.count
    
    print(f"\n📊 Alertas antiguas (>{dias} días):")
    print(f"   ✅ Resueltas: {resueltas.count}")
    print(f"   🗑️  Descartadas: {descartadas.count}")
    print(f"   📋 Total a eliminar: {total}")
    
    if total == 0:
        print("\n✅ No hay alertas antiguas para eliminar")
        return
    
    print(f"\n⏳ Eliminando {total} alertas...")
    
    try:
        # Eliminar resueltas
        if resueltas.count > 0:
            supabase.table("alertas")\
                .delete()\
                .eq("estado", "resuelto")\
                .lt("fecha_creacion", fecha_limite)\
                .execute()
        
        # Eliminar descartadas
        if descartadas.count > 0:
            supabase.table("alertas")\
                .delete()\
                .eq("estado", "descartada")\
                .lt("fecha_creacion", fecha_limite)\
                .execute()
        
        print(f"✅ ¡Limpieza completada! {total} alertas eliminadas")
    except Exception as e:
        print(f"❌ Error: {e}")

def limpiar_alertas_peso_inactivo(confirmar=False):
    """Elimina TODAS las alertas de 'Sistema de peso inactivo'"""
    if not confirmar:
        print("\n⚠️  Esta función eliminará TODAS las alertas de 'Sistema de peso inactivo'")
        print("Para confirmar, ejecuta con --confirmar")
        return
    
    # Contar
    alertas = supabase.table("alertas")\
        .select("id", count="exact")\
        .ilike("titulo", "%Sistema de peso inactivo%")\
        .execute()
    
    total = alertas.count
    
    print(f"\n📊 Alertas de 'Sistema de peso inactivo': {total}")
    
    if total == 0:
        print("\n✅ No hay alertas para eliminar")
        return
    
    print(f"\n⏳ Eliminando {total} alertas...")
    
    try:
        supabase.table("alertas")\
            .delete()\
            .ilike("titulo", "%Sistema de peso inactivo%")\
            .execute()
        
        print(f"✅ ¡Limpieza completada! {total} alertas eliminadas")
    except Exception as e:
        print(f"❌ Error: {e}")

def limpiar_alertas_sin_idproducto(confirmar=False):
    """Elimina alertas de productos que no tienen idproducto asignado"""
    if not confirmar:
        print("\n⚠️  Esta función eliminará alertas de productos sin idproducto")
        print("Para confirmar, ejecuta con --confirmar")
        return
    
    # Contar alertas con título de producto pero sin idproducto
    alertas = supabase.table("alertas")\
        .select("*")\
        .is_("idproducto", "null")\
        .execute().data or []
    
    # Filtrar solo alertas que deberían tener idproducto
    alertas_productos = [a for a in alertas if any(keyword in a.get("titulo", "").lower() 
                        for keyword in ["producto", "stock", "vencimiento"])]
    
    total = len(alertas_productos)
    
    print(f"\n📊 Alertas de productos sin idproducto: {total}")
    
    if total == 0:
        print("\n✅ No hay alertas para eliminar")
        return
    
    print(f"\n⏳ Eliminando {total} alertas...")
    
    ids = [a["id"] for a in alertas_productos]
    
    try:
        supabase.table("alertas")\
            .delete()\
            .in_("id", ids)\
            .execute()
        
        print(f"✅ ¡Limpieza completada! {total} alertas eliminadas")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    confirmar = "--confirmar" in sys.argv
    
    print("\n" + "="*80)
    print("🧹 LIMPIEZA AVANZADA DE ALERTAS")
    print("="*80)
    
    if "--antiguas" in sys.argv:
        dias = 7
        if "--dias" in sys.argv:
            idx = sys.argv.index("--dias")
            if idx + 1 < len(sys.argv):
                dias = int(sys.argv[idx + 1])
        limpiar_alertas_resueltas_antiguas(dias=dias, confirmar=confirmar)
    
    elif "--peso-inactivo" in sys.argv:
        limpiar_alertas_peso_inactivo(confirmar=confirmar)
    
    elif "--sin-idproducto" in sys.argv:
        limpiar_alertas_sin_idproducto(confirmar=confirmar)
    
    else:
        print("\n📖 OPCIONES DISPONIBLES:")
        print("\n1️⃣  Limpiar alertas resueltas/descartadas antiguas (>7 días):")
        print("   python scripts/limpiar_alertas_avanzado.py --antiguas --confirmar")
        print("   python scripts/limpiar_alertas_avanzado.py --antiguas --dias 30 --confirmar")
        
        print("\n2️⃣  Eliminar TODAS las alertas 'Sistema de peso inactivo':")
        print("   python scripts/limpiar_alertas_avanzado.py --peso-inactivo --confirmar")
        
        print("\n3️⃣  Eliminar alertas de productos sin idproducto:")
        print("   python scripts/limpiar_alertas_avanzado.py --sin-idproducto --confirmar")
        print("\n" + "="*80)
