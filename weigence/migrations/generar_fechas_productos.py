"""
Script para generar fechas de elaboración y vencimiento para productos existentes
Ejecutar: python migrations/generar_fechas_productos.py
"""

import os
import sys
from datetime import datetime, timedelta
import random

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.conexion_supabase import supabase

# Configuración de vida útil por categoría (en meses)
VIDA_UTIL_POR_CATEGORIA = {
    'Antiinflamatorio': (18, 36),      # 1.5 a 3 años
    'Antibiótico': (24, 36),           # 2 a 3 años
    'Suplemento': (12, 24),            # 1 a 2 años
    'Antihistamínico': (24, 36),       # 2 a 3 años
    'Broncodilatador': (24, 36),       # 2 a 3 años
    'Analgésico': (18, 36),            # 1.5 a 3 años
    'Antidiabetico': (24, 36),         # 2 a 3 años
    'Antihipertensivo': (24, 36),      # 2 a 3 años
    'Dermocosmética': (12, 24),        # 1 a 2 años
    'Desinfectante': (24, 36),         # 2 a 3 años
    'Primeros Auxilios': (12, 36),     # 1 a 3 años
    'Equipamiento': (36, 60),          # 3 a 5 años
    'Higiene': (12, 24),               # 1 a 2 años
}

def generar_fechas_realistas(categoria):
    """
    Genera fechas de elaboración y vencimiento realistas según la categoría
    """
    # Obtener rango de vida útil para la categoría
    vida_util = VIDA_UTIL_POR_CATEGORIA.get(categoria, (12, 24))
    
    # Fecha de elaboración: entre 6 y 18 meses atrás
    meses_atras = random.randint(6, 18)
    fecha_elaboracion = datetime.now() - timedelta(days=meses_atras * 30)
    
    # Vida útil del producto en meses
    vida_util_meses = random.randint(vida_util[0], vida_util[1])
    
    # Fecha de vencimiento
    fecha_vencimiento = fecha_elaboracion + timedelta(days=vida_util_meses * 30)
    
    return fecha_elaboracion.date(), fecha_vencimiento.date()

def calcular_dias_restantes(fecha_vencimiento):
    """Calcula días restantes hasta el vencimiento"""
    hoy = datetime.now().date()
    return (fecha_vencimiento - hoy).days

def generar_sql_updates():
    """
    Genera SQL UPDATE statements para agregar fechas a productos existentes
    """
    print("🔍 Consultando productos de Supabase...")
    
    try:
        # Obtener todos los productos
        response = supabase.table("productos").select("idproducto, nombre, categoria").execute()
        productos = response.data
        
        if not productos:
            print("❌ No se encontraron productos en la base de datos")
            return
        
        print(f"✅ Se encontraron {len(productos)} productos\n")
        print("=" * 80)
        print("📝 SQL UPDATES GENERADOS:")
        print("=" * 80)
        print("\n-- Copiar y pegar en Supabase SQL Editor:\n")
        
        # Contador de estados
        vencidos = 0
        criticos = 0
        proximos = 0
        vigentes = 0
        
        sql_statements = []
        
        for producto in productos:
            id_producto = producto['idproducto']
            nombre = producto['nombre']
            categoria = producto.get('categoria', 'General')
            
            # Generar fechas
            fecha_elab, fecha_venc = generar_fechas_realistas(categoria)
            dias_restantes = calcular_dias_restantes(fecha_venc)
            
            # Determinar estado
            if dias_restantes < 0:
                estado = "🔴 VENCIDO"
                vencidos += 1
            elif dias_restantes <= 7:
                estado = f"🟠 CRÍTICO ({dias_restantes}d)"
                criticos += 1
            elif dias_restantes <= 30:
                estado = f"🟡 PRÓXIMO ({dias_restantes}d)"
                proximos += 1
            else:
                estado = f"🟢 VIGENTE ({dias_restantes}d)"
                vigentes += 1
            
            # Generar SQL UPDATE
            sql = f"UPDATE productos SET fecha_elaboracion = '{fecha_elab}', fecha_vencimiento = '{fecha_venc}' WHERE idproducto = {id_producto};"
            sql_statements.append(sql)
            
            # Imprimir información
            print(f"-- {nombre} ({categoria}) - {estado}")
            print(f"--   Elaboración: {fecha_elab.strftime('%d/%m/%Y')} | Vencimiento: {fecha_venc.strftime('%d/%m/%Y')}")
            print(sql)
            print()
        
        # Resumen
        print("\n" + "=" * 80)
        print("📊 RESUMEN:")
        print("=" * 80)
        print(f"Total de productos: {len(productos)}")
        print(f"🔴 Vencidos: {vencidos}")
        print(f"🟠 Críticos (≤7 días): {criticos}")
        print(f"🟡 Próximos (≤30 días): {proximos}")
        print(f"🟢 Vigentes (>30 días): {vigentes}")
        print("=" * 80)
        
        # Guardar en archivo
        output_file = "migrations/update_fechas_productos.sql"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("-- Actualización de fechas de elaboración y vencimiento\n")
            f.write("-- Generado automáticamente\n")
            f.write(f"-- Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("BEGIN;\n\n")
            f.write('\n'.join(sql_statements))
            f.write("\n\nCOMMIT;\n")
        
        print(f"\n✅ Archivo generado: {output_file}")
        print("📋 Copia y pega el contenido en Supabase SQL Editor")
        
    except Exception as e:
        print(f"❌ Error al consultar Supabase: {e}")
        print("\n💡 Asegúrate de que:")
        print("   1. Las variables SUPABASE_URL y SUPABASE_KEY están en .env")
        print("   2. La conexión a Supabase funciona correctamente")

if __name__ == "__main__":
    print("🚀 Generador de Fechas de Vencimiento")
    print("=" * 80)
    generar_sql_updates()
