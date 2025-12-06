"""
Script de prueba para verificar exportación Excel de Inventario y Ventas
"""

import sys
import os
from datetime import datetime

# Agregar el path del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.excel_exporter import ExcelExporter

def test_exportador_inventario():
    """Prueba exportación de inventario"""
    
    print("🧪 Probando exportación de INVENTARIO...")
    
    # Datos de prueba
    productos_test = [
        {
            'codigo_producto': 'PARA500',
            'nombre': 'Paracetamol 500mg',
            'categoria': 'Analgésicos',
            'stock': 0,
            'stock_minimo': 10,
            'peso': 0.05,
            'id_estante': 'E01',
            'fecha_ingreso': '2025-11-01T10:00:00'
        },
        {
            'codigo_producto': 'IBU400',
            'nombre': 'Ibuprofeno 400mg',
            'categoria': 'Antiinflamatorios',
            'stock': 5,
            'stock_minimo': 15,
            'peso': 0.08,
            'id_estante': 'E02',
            'fecha_ingreso': '2025-11-15T14:30:00'
        },
        {
            'codigo_produto': 'AMOX500',
            'nombre': 'Amoxicilina 500mg',
            'categoria': 'Antibióticos',
            'stock': 50,
            'stock_minimo': 20,
            'peso': 0.12,
            'id_estante': 'E03',
            'fecha_ingreso': '2025-12-01T09:00:00'
        },
        {
            'codigo_producto': 'LORA10',
            'nombre': 'Loratadina 10mg',
            'categoria': 'Antihistamínicos',
            'stock': 100,
            'stock_minimo': 30,
            'peso': 0.03,
            'id_estante': 'E04',
            'fecha_ingreso': '2025-11-20T11:15:00'
        },
        {
            'codigo_producto': 'DICLO50',
            'nombre': 'Diclofenaco 50mg',
            'categoria': 'Antiinflamatorios',
            'stock': 8,
            'stock_minimo': 10,
            'peso': 0.06,
            'id_estante': 'E02',
            'fecha_ingreso': '2025-12-03T16:00:00'
        }
    ]
    
    filtros_test = {
        'categoria': 'Todas',
        'estado': 'Todos'
    }
    
    try:
        exporter = ExcelExporter()
        excel_file = exporter.exportar_inventario(productos_test, filtros_test)
        
        output_path = os.path.join(
            os.path.dirname(__file__), 
            f'TEST_Inventario_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
        
        with open(output_path, 'wb') as f:
            f.write(excel_file.getvalue())
        
        file_size = os.path.getsize(output_path)
        
        print("="*60)
        print("🎉 INVENTARIO - PRUEBA EXITOSA")
        print("="*60)
        print(f"📦 Productos exportados: {len(productos_test)}")
        print(f"📁 Archivo: {os.path.basename(output_path)}")
        print(f"💾 Tamaño: {file_size / 1024:.2f} KB")
        print()
        
        return output_path
        
    except Exception as e:
        print(f"\n❌ ERROR en exportación de inventario:")
        print(f"   {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_exportador_ventas():
    """Prueba exportación de ventas"""
    
    print("🧪 Probando exportación de VENTAS...")
    
    # Datos de prueba
    ventas_test = [
        {
            'id_venta': 1,
            'fecha': '2025-12-05T10:15:00',
            'vendedor_rut': '21321316-9',
            'vendedor_nombre': 'Nelson Duarte',
            'total': 15500.50,
            'total_productos': 3,
            'total_unidades': 15
        },
        {
            'id_venta': 2,
            'fecha': '2025-12-05T11:30:00',
            'vendedor_rut': '12345678-9',
            'vendedor_nombre': 'María González',
            'total': 8750.00,
            'total_productos': 2,
            'total_unidades': 8
        },
        {
            'id_venta': 3,
            'fecha': '2025-12-04T15:45:00',
            'vendedor_rut': '21321316-9',
            'vendedor_nombre': 'Nelson Duarte',
            'total': 23400.75,
            'total_productos': 5,
            'total_unidades': 25
        },
        {
            'id_venta': 4,
            'fecha': '2025-12-04T09:20:00',
            'vendedor_rut': '98765432-1',
            'vendedor_nombre': 'Pedro Sánchez',
            'total': 12300.00,
            'total_productos': 4,
            'total_unidades': 18
        },
        {
            'id_venta': 5,
            'fecha': '2025-12-03T14:00:00',
            'vendedor_rut': '12345678-9',
            'vendedor_nombre': 'María González',
            'total': 5600.50,
            'total_productos': 1,
            'total_unidades': 5
        }
    ]
    
    filtros_test = {
        'fechaDesde': '2025-12-01',
        'fechaHasta': '2025-12-05'
    }
    
    try:
        exporter = ExcelExporter()
        excel_file = exporter.exportar_ventas(ventas_test, filtros_test)
        
        output_path = os.path.join(
            os.path.dirname(__file__), 
            f'TEST_Ventas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
        
        with open(output_path, 'wb') as f:
            f.write(excel_file.getvalue())
        
        file_size = os.path.getsize(output_path)
        
        print("="*60)
        print("🎉 VENTAS - PRUEBA EXITOSA")
        print("="*60)
        print(f"💰 Ventas exportadas: {len(ventas_test)}")
        print(f"📁 Archivo: {os.path.basename(output_path)}")
        print(f"💾 Tamaño: {file_size / 1024:.2f} KB")
        print()
        
        return output_path
        
    except Exception as e:
        print(f"\n❌ ERROR en exportación de ventas:")
        print(f"   {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Ejecuta todas las pruebas"""
    print("\n" + "="*60)
    print("🚀 PRUEBA DE EXPORTACIÓN EXCEL - SISTEMA WEIGENCE")
    print("="*60)
    print()
    
    # Probar inventario
    inventario_path = test_exportador_inventario()
    
    # Probar ventas
    ventas_path = test_exportador_ventas()
    
    # Resumen final
    print("="*60)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*60)
    
    if inventario_path:
        print(f"✅ Inventario: {os.path.basename(inventario_path)}")
    else:
        print("❌ Inventario: FALLÓ")
    
    if ventas_path:
        print(f"✅ Ventas: {os.path.basename(ventas_path)}")
    else:
        print("❌ Ventas: FALLÓ")
    
    print()
    print("💡 Los archivos se encuentran en la carpeta 'weigence'")
    print("💡 Puedes abrirlos con Excel, LibreOffice o Google Sheets")
    print()
    
    # Abrir archivos automáticamente (opcional)
    if inventario_path and ventas_path:
        try:
            import subprocess
            print("🔓 Abriendo archivos generados...")
            if os.name == 'nt':  # Windows
                os.startfile(inventario_path)
                os.startfile(ventas_path)
            else:  # macOS/Linux
                subprocess.call(['open', inventario_path])
                subprocess.call(['open', ventas_path])
        except:
            pass
    
    return inventario_path is not None and ventas_path is not None


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
