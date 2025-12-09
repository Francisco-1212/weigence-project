"""
Script para limpiar alertas duplicadas de discrepancia de peso
Mantiene solo la alerta más reciente de cada grupo duplicado
"""
import sys
import os

# Añadir el directorio raíz al path para imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.conexion_supabase import supabase
from datetime import datetime
from collections import defaultdict

def analizar_alertas_duplicadas():
    """Analiza y muestra estadísticas de alertas duplicadas"""
    print("\n" + "="*70)
    print("🔍 ANÁLISIS DE ALERTAS DUPLICADAS")
    print("="*70 + "\n")
    
    # Obtener TODAS las alertas pendientes (no solo de peso)
    alertas = supabase.table("alertas")\
        .select("*")\
        .eq("estado", "pendiente")\
        .order("fecha_creacion", desc=True)\
        .execute().data or []
    
    print(f"📊 Total de alertas pendientes: {len(alertas)}")
    
    # Agrupar por título + (id_estante O idproducto según corresponda)
    grupos = defaultdict(list)
    for alerta in alertas:
        # Usar id_estante para alertas de peso, idproducto para alertas de productos
        id_referencia = alerta.get("id_estante") if alerta.get("id_estante") else alerta.get("idproducto")
        clave = (alerta.get("titulo"), id_referencia)
        grupos[clave].append(alerta)
    
    # Identificar duplicados
    duplicados = {k: v for k, v in grupos.items() if len(v) > 1}
    
    if duplicados:
        print(f"\n⚠️  Grupos con duplicados encontrados: {len(duplicados)}")
        print(f"🔴 Total de alertas duplicadas a eliminar: {sum(len(v) - 1 for v in duplicados.values())}")
        print(f"✅ Alertas únicas que se mantendrán: {len(duplicados)}")
        
        print("\n" + "-"*70)
        print("📋 DETALLE DE DUPLICADOS:")
        print("-"*70)
        
        for idx, (clave, alertas_grupo) in enumerate(duplicados.items(), 1):
            titulo, id_referencia = clave
            print(f"\n{idx}. {titulo}")
            if id_referencia:
                # Determinar si es estante o producto
                tipo = "Estante ID" if any("peso" in titulo.lower() for _ in [titulo]) else "Producto ID"
                print(f"   {tipo}: {id_referencia}")
            print(f"   Cantidad de duplicados: {len(alertas_grupo)}")
            
            for i, alerta in enumerate(alertas_grupo):
                fecha = alerta.get("fecha_creacion", "Sin fecha")
                estado = "🆕 MÁS RECIENTE" if i == 0 else "🗑️  A ELIMINAR"
                print(f"      {estado} - ID: {alerta['id']} - Fecha: {fecha}")
    else:
        print("\n✅ No se encontraron alertas duplicadas. ¡Todo está limpio!")
    
    return duplicados

def limpiar_alertas_duplicadas(modo_prueba=True):
    """
    Elimina alertas duplicadas, manteniendo solo la más reciente de cada grupo
    
    Args:
        modo_prueba: Si es True, solo muestra qué se eliminaría sin hacer cambios
    """
    duplicados = analizar_alertas_duplicadas()
    
    if not duplicados:
        return
    
    print("\n" + "="*70)
    if modo_prueba:
        print("🧪 MODO PRUEBA - NO SE REALIZARÁN CAMBIOS")
    else:
        print("⚠️  MODO EJECUCIÓN - SE ELIMINARÁN LAS ALERTAS DUPLICADAS")
    print("="*70 + "\n")
    
    ids_a_eliminar = []
    ids_a_mantener = []
    
    for clave, alertas_grupo in duplicados.items():
        # Ordenar por fecha (más reciente primero)
        alertas_ordenadas = sorted(
            alertas_grupo, 
            key=lambda x: x.get("fecha_creacion", ""), 
            reverse=True
        )
        
        # Mantener la primera (más reciente)
        ids_a_mantener.append(alertas_ordenadas[0]["id"])
        
        # Marcar el resto para eliminación
        for alerta in alertas_ordenadas[1:]:
            ids_a_eliminar.append(alerta["id"])
    
    print(f"📊 Resumen:")
    print(f"   ✅ Alertas a mantener: {len(ids_a_mantener)}")
    print(f"   🗑️  Alertas a eliminar: {len(ids_a_eliminar)}")
    
    if modo_prueba:
        print(f"\n💡 IDs que se eliminarían: {ids_a_eliminar[:10]}{'...' if len(ids_a_eliminar) > 10 else ''}")
        print(f"\n✅ Para ejecutar la limpieza real, ejecuta:")
        print(f"   python scripts/limpiar_alertas_duplicadas.py --ejecutar")
    else:
        print(f"\n⏳ Eliminando {len(ids_a_eliminar)} alertas duplicadas...")
        
        # Eliminar en lotes de 100 para evitar timeouts
        lote_size = 100
        total_eliminadas = 0
        
        for i in range(0, len(ids_a_eliminar), lote_size):
            lote = ids_a_eliminar[i:i+lote_size]
            try:
                # OPCIÓN 1: Eliminar permanentemente (DELETE)
                # supabase.table("alertas").delete().in_("id", lote).execute()
                
                # OPCIÓN 2: Marcar como "descartada" (RECOMENDADO - mantiene historial)
                supabase.table("alertas").update({
                    "estado": "descartada",
                    "fecha_modificacion": datetime.now().isoformat()
                }).in_("id", lote).execute()
                
                total_eliminadas += len(lote)
                print(f"   ✅ Procesadas {total_eliminadas}/{len(ids_a_eliminar)} alertas...")
            except Exception as e:
                print(f"   ❌ Error procesando lote: {e}")
        
        print(f"\n✅ ¡Limpieza completada!")
        print(f"   🗑️  Total de alertas duplicadas eliminadas: {total_eliminadas}")
        print(f"   ✅ Alertas únicas mantenidas: {len(ids_a_mantener)}")

def limpiar_todas_las_alertas_peso(confirmar=False):
    """
    Opción nuclear: Elimina TODAS las alertas de discrepancia de peso
    Útil si quieres empezar desde cero
    """
    if not confirmar:
        print("\n⚠️  ADVERTENCIA: Esta función eliminará TODAS las alertas de discrepancia de peso")
        print("Para confirmar, ejecuta:")
        print("  python scripts/limpiar_alertas_duplicadas.py --limpiar-todo --confirmar")
        return
    
    print("\n" + "="*70)
    print("🔴 LIMPIEZA TOTAL DE ALERTAS DE DISCREPANCIA DE PESO")
    print("="*70 + "\n")
    
    # Contar alertas
    alertas = supabase.table("alertas")\
        .select("id")\
        .eq("estado", "pendiente")\
        .ilike("titulo", "%Discrepancia de peso%")\
        .execute().data or []
    
    total = len(alertas)
    print(f"📊 Total de alertas a eliminar: {total}")
    
    if total == 0:
        print("✅ No hay alertas para eliminar")
        return
    
    print(f"\n⏳ Eliminando {total} alertas...")
    
    try:
        # Marcar como descartadas (mantiene historial)
        supabase.table("alertas").update({
            "estado": "descartada",
            "fecha_modificacion": datetime.now().isoformat()
        }).eq("estado", "pendiente")\
        .ilike("titulo", "%Discrepancia de peso%")\
        .execute()
        
        print(f"✅ ¡Limpieza completada! {total} alertas eliminadas")
        print(f"\n💡 Las nuevas alertas se generarán automáticamente basadas en")
        print(f"   las discrepancias de peso ACTUALES en los estantes.")
    except Exception as e:
        print(f"❌ Error: {e}")

def limpiar_todas_las_alertas_pendientes(confirmar=False):
    """
    Opción nuclear total: Elimina TODAS las alertas pendientes
    Útil para resetear completamente el sistema de alertas
    """
    if not confirmar:
        print("\n⚠️  ADVERTENCIA: Esta función eliminará TODAS las alertas pendientes")
        print("Para confirmar, ejecuta:")
        print("  python scripts/limpiar_alertas_duplicadas.py --resetear-todo --confirmar")
        return
    
    print("\n" + "="*70)
    print("🔴 LIMPIEZA TOTAL DE TODAS LAS ALERTAS PENDIENTES")
    print("="*70 + "\n")
    
    # Contar alertas
    alertas = supabase.table("alertas")\
        .select("id")\
        .eq("estado", "pendiente")\
        .execute().data or []
    
    total = len(alertas)
    print(f"📊 Total de alertas a eliminar: {total}")
    
    if total == 0:
        print("✅ No hay alertas para eliminar")
        return
    
    print(f"\n⏳ Eliminando {total} alertas...")
    
    try:
        # Marcar como descartadas (mantiene historial)
        supabase.table("alertas").update({
            "estado": "descartada",
            "fecha_modificacion": datetime.now().isoformat()
        }).eq("estado", "pendiente")\
        .execute()
        
        print(f"✅ ¡Limpieza completada! {total} alertas eliminadas")
        print(f"\n💡 Las nuevas alertas se generarán automáticamente basadas en")
        print(f"   las condiciones ACTUALES (stock, vencimientos, peso, etc.).")
    except Exception as e:
        print(f"❌ Error: {e}")

def mostrar_estadisticas_generales():
    """Muestra estadísticas generales de la tabla de alertas"""
    print("\n" + "="*70)
    print("📊 ESTADÍSTICAS GENERALES DE ALERTAS")
    print("="*70 + "\n")
    
    try:
        # Total de alertas
        total = supabase.table("alertas").select("id", count="exact").execute()
        print(f"📋 Total de alertas en la base de datos: {total.count}")
        
        # Por estado
        estados = supabase.table("alertas")\
            .select("estado")\
            .execute().data or []
        
        from collections import Counter
        conteo_estados = Counter(a.get("estado") for a in estados)
        
        print(f"\n📊 Por estado:")
        for estado, cantidad in conteo_estados.items():
            emoji = "🟢" if estado == "pendiente" else "✅" if estado == "resuelto" else "🗑️"
            print(f"   {emoji} {estado}: {cantidad}")
        
        # Alertas de peso
        peso = supabase.table("alertas")\
            .select("id")\
            .eq("estado", "pendiente")\
            .ilike("titulo", "%Discrepancia de peso%")\
            .execute().data or []
        
        print(f"\n⚖️  Alertas de discrepancia de peso pendientes: {len(peso)}")
        
        # Alertas de productos vencidos
        vencidos = supabase.table("alertas")\
            .select("id")\
            .eq("estado", "pendiente")\
            .ilike("titulo", "%vencido%")\
            .execute().data or []
        
        print(f"⏰ Alertas de productos vencidos pendientes: {len(vencidos)}")
        
        # Alertas de stock bajo
        stock = supabase.table("alertas")\
            .select("id")\
            .eq("estado", "pendiente")\
            .ilike("titulo", "%stock%")\
            .execute().data or []
        
        print(f"📦 Alertas de stock bajo/agotado pendientes: {len(stock)}")
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")

if __name__ == "__main__":
    import sys
    
    # Verificar argumentos
    if "--ejecutar" in sys.argv:
        limpiar_alertas_duplicadas(modo_prueba=False)
    elif "--limpiar-todo" in sys.argv:
        confirmar = "--confirmar" in sys.argv
        limpiar_todas_las_alertas_peso(confirmar=confirmar)
    elif "--resetear-todo" in sys.argv:
        confirmar = "--confirmar" in sys.argv
        limpiar_todas_las_alertas_pendientes(confirmar=confirmar)
    elif "--stats" in sys.argv:
        mostrar_estadisticas_generales()
    else:
        # Modo prueba por defecto
        print("\n🔍 Ejecutando análisis en MODO PRUEBA...")
        print("   (No se realizarán cambios en la base de datos)\n")
        limpiar_alertas_duplicadas(modo_prueba=True)
        
        print("\n" + "="*70)
        print("📖 OPCIONES DISPONIBLES:")
        print("="*70)
        print("\n1️⃣  Análisis sin cambios (ACTUAL):")
        print("   python scripts/limpiar_alertas_duplicadas.py")
        print("\n2️⃣  Eliminar solo duplicados (mantener 1 por grupo) - RECOMENDADO:")
        print("   python scripts/limpiar_alertas_duplicadas.py --ejecutar")
        print("\n3️⃣  Eliminar TODAS las alertas de peso:")
        print("   python scripts/limpiar_alertas_duplicadas.py --limpiar-todo --confirmar")
        print("\n4️⃣  Eliminar TODAS las alertas pendientes (reseteo total):")
        print("   python scripts/limpiar_alertas_duplicadas.py --resetear-todo --confirmar")
        print("\n5️⃣  Ver estadísticas generales:")
        print("   python scripts/limpiar_alertas_duplicadas.py --stats")
        print("\n" + "="*70)
        print("\n💡 RECOMENDACIÓN: Usa la opción 2️⃣  para eliminar duplicados")
        print("   manteniendo una alerta por cada problema real.\n")
