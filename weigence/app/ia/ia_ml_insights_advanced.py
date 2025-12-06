"""
Análisis ML Avanzado - Insights específicos y accionables
Genera mensajes contextuales basados en análisis profundo de datos reales

Schema real de Supabase:
- detalle_ventas: iddetalle, idventa, idproducto, cantidad, precio_unitario, subtotal, fecha_detalle
- productos: idproducto, nombre, categoria, stock, descripcion, peso, fecha_ingreso, ingresado_por, modificado_por, fecha_modificacion, id_estante, precio_unitario
- ventas: idventa, rut_usuario, fecha_venta, total
- alertas: id, titulo, descripcion, icono, tipo_color, fecha_creacion, estado, idproducto, idusuario
- movimientos_inventario: id_movimiento, idproducto, id_estante, rut_usuario, cantidad, tipo_evento, timestamp, observacion
- auditoria_eventos: id, fecha, usuario, accion, detalle
- estantes: id_estante, categoria, coord_x, coord_y, peso_maximo, nombre, peso_actual, estado, ultima_actualizacion
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# Import dinámico para evitar circular dependency
def _get_supabase():
    """Obtiene cliente Supabase de forma lazy."""
    from api.conexion_supabase import supabase
    return supabase


class AdvancedMLInsights:
    """Genera insights específicos basados en análisis ML de datos reales."""
    
    def __init__(self):
        self.supabase = _get_supabase()
    
    # ==================== DASHBOARD ====================
    
    def analyze_dashboard_rankings(self) -> Dict[str, any]:
        """Analiza top productos vendidos y menos vendidos."""
        try:
            # Top 5 más vendidos últimas 48h
            response = self.supabase.table('detalle_ventas') \
                .select('productos(nombre), cantidad') \
                .gte('fecha_detalle', (datetime.now() - timedelta(hours=48)).isoformat()) \
                .execute()
            
            if response.data:
                # Agrupar por producto
                product_sales = {}
                for item in response.data:
                    if item.get('productos'):
                        prod_name = item['productos']['nombre']
                        qty = float(item.get('cantidad', 0))
                        product_sales[prod_name] = product_sales.get(prod_name, 0) + qty
                
                # Top 5 y Bottom 5
                sorted_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)
                
                return {
                    'top_5': sorted_products[:5] if len(sorted_products) >= 5 else sorted_products,
                    'bottom_5': sorted_products[-5:] if len(sorted_products) >= 5 else [],
                    'total_products': len(sorted_products)
                }
        except Exception as e:
            logger.error(f"Error analizando rankings: {e}")
        
        return {'top_5': [], 'bottom_5': [], 'total_products': 0}
    
    # ==================== INVENTARIO ====================
    
    def analyze_inventory_capacity(self) -> Dict[str, any]:
        """Detecta estantes con capacidad excedida o productos sin stock."""
        try:
            # Productos sin stock o con stock bajo
            response = self.supabase.table('productos') \
                .select('nombre, stock, id_estante') \
                .execute()
            
            products_without_stock = []
            products_below_min = []
            above_max = []
            
            if response.data:
                for prod in response.data:
                    stock = int(prod.get('stock', 0))
                    nombre = prod.get('nombre', 'Producto sin nombre')
                    id_estante = prod.get('id_estante')
                    
                    if stock <= 0:
                        products_without_stock.append(nombre)
                    elif stock <= 5:  # Umbral bajo (configurable)
                        products_below_min.append({
                            'nombre': nombre,
                            'stock': stock,
                            'min': 5,
                            'ubicacion': f"Estante {id_estante}" if id_estante else "Sin asignar"
                        })
            
            # Estantes con peso excedido - CALCULAR PESO REAL desde productos
            estantes_response = self.supabase.table('estantes') \
                .select('id_estante, nombre, peso_maximo') \
                .execute()
            
            shelves_exceeded = []
            if estantes_response.data:
                # Obtener productos por estante para calcular peso real
                productos_response = self.supabase.table('productos') \
                    .select('id_estante, peso, stock') \
                    .execute()
                
                # Calcular peso actual por estante
                peso_por_estante = {}
                if productos_response.data:
                    for prod in productos_response.data:
                        id_est = prod.get('id_estante')
                        if id_est:
                            peso = float(prod.get('peso', 0))
                            stock = float(prod.get('stock', 0))
                            # CORRECCIÓN: Los pesos en BD están en gramos * 1000, dividir por 1000
                            # Para convertir a kg reales, dividir entre 1000
                            peso_kg_real = peso / 1000  # Convertir a kg
                            peso_total = peso_kg_real * stock
                            
                            if id_est not in peso_por_estante:
                                peso_por_estante[id_est] = 0
                            peso_por_estante[id_est] += peso_total
                
                for shelf in estantes_response.data:
                    id_estante = shelf['id_estante']
                    peso_actual = peso_por_estante.get(id_estante, 0)
                    peso_max = float(shelf.get('peso_maximo', 0))
                    
                    if peso_max > 0 and peso_actual > peso_max:
                        shelves_exceeded.append({
                            'nombre': shelf.get('nombre', f"Estante {id_estante}"),
                            'actual': peso_actual,
                            'maximo': peso_max,
                            'exceso_porcentaje': round(((peso_actual - peso_max) / peso_max) * 100, 1)
                        })
            
            return {
                'without_stock': products_without_stock,
                'below_min': products_below_min,
                'below_minimum': products_below_min,  # Alias
                'above_max': above_max,
                'shelves_exceeded': shelves_exceeded,
                'total_issues': len(products_without_stock) + len(products_below_min) + len(shelves_exceeded)
            }
            
        except Exception as e:
            logger.error(f"Error analizando capacidad inventario: {e}")
        
        return {
            'without_stock': [],
            'below_min': [],
            'below_minimum': [],
            'above_max': [],
            'shelves_exceeded': [],
            'total_issues': 0
        }
    
    # ==================== MOVIMIENTOS ====================
    
    def analyze_unjustified_movements(self) -> Dict[str, any]:
        """Detecta retiros de inventario sin justificación."""
        try:
            # Retiros últimas 24h
            response = self.supabase.table('movimientos_inventario') \
                .select('id_movimiento, idproducto, productos(nombre), cantidad, timestamp, observacion') \
                .eq('tipo_evento', 'retiro') \
                .gte('timestamp', (datetime.now() - timedelta(hours=24)).isoformat()) \
                .execute()
            
            unjustified = []
            
            if response.data:
                for movement in response.data:
                    # Si no tiene observación válida, es no justificado
                    obs = movement.get('observacion', '').strip()
                    
                    if not obs or obs.lower() in ['', 'ninguna', 'n/a']:
                        prod_name = movement.get('productos', {}).get('nombre', 'Producto desconocido') if movement.get('productos') else f"ID {movement['idproducto']}"
                        
                        unjustified.append({
                            'producto': prod_name,
                            'cantidad': float(movement.get('cantidad', 0)),
                            'timestamp': movement.get('timestamp'),
                            'id_movimiento': movement.get('id_movimiento')
                        })
            
            return {
                'unjustified': unjustified,
                'total_unjustified': len(unjustified)
            }
            
        except Exception as e:
            logger.error(f"Error analizando movimientos no justificados: {e}")
        
        return {'unjustified': [], 'total_unjustified': 0}
    
    # ==================== VENTAS ====================
    
    def analyze_sales_comparison_48h(self) -> Dict[str, any]:
        """Compara ventas últimas 24h vs 24h anteriores."""
        try:
            now = datetime.now()
            last_24h = now - timedelta(hours=24)
            previous_48h = now - timedelta(hours=48)
            
            # Ventas últimas 24h
            recent_response = self.supabase.table('ventas') \
                .select('total') \
                .gte('fecha_venta', last_24h.isoformat()) \
                .execute()
            
            # Ventas 24-48h atrás
            previous_response = self.supabase.table('ventas') \
                .select('total') \
                .gte('fecha_venta', previous_48h.isoformat()) \
                .lt('fecha_venta', last_24h.isoformat()) \
                .execute()
            
            recent_total = sum(float(v.get('total', 0)) for v in recent_response.data) if recent_response.data else 0
            previous_total = sum(float(v.get('total', 0)) for v in previous_response.data) if previous_response.data else 0
            
            if previous_total > 0:
                change_percent = round(((recent_total - previous_total) / previous_total) * 100, 1)
            else:
                change_percent = 100.0 if recent_total > 0 else 0.0
            
            # Obtener producto más vendido
            top_product_name = 'N/A'
            top_product_qty = 0
            
            try:
                detalle_response = self.supabase.table('detalle_ventas') \
                    .select('productos(nombre), cantidad') \
                    .gte('fecha_detalle', last_24h.isoformat()) \
                    .execute()
                
                if detalle_response.data:
                    product_sales = {}
                    for item in detalle_response.data:
                        if item.get('productos'):
                            prod_name = item['productos']['nombre']
                            qty = float(item.get('cantidad', 0))
                            product_sales[prod_name] = product_sales.get(prod_name, 0) + qty
                    
                    if product_sales:
                        top_product = max(product_sales.items(), key=lambda x: x[1])
                        top_product_name = top_product[0]
                        top_product_qty = top_product[1]
            except Exception as e:
                logger.debug(f"No se pudo obtener top producto: {e}")
            
            return {
                'recent_total': recent_total,
                'previous_total': previous_total,
                'change_percent': change_percent,
                'is_increase': recent_total > previous_total,
                'top_product': top_product_name,
                'top_product_qty': top_product_qty
            }
            
        except Exception as e:
            logger.error(f"Error comparando ventas 48h: {e}")
        
        return {
            'recent_total': 0,
            'previous_total': 0,
            'change_percent': 0,
            'is_increase': False,
            'top_product': 'N/A',
            'top_product_qty': 0
        }
    
    # ==================== ALERTAS ====================
    
    def analyze_critical_alerts_resolution(self) -> Dict[str, any]:
        """Obtiene alertas críticas activas con planes de resolución."""
        try:
            # Obtener alertas críticas (rojo, amarilla/amarillo, naranja)
            response = self.supabase.table('alertas') \
                .select('id, titulo, descripcion, tipo_color, idproducto, productos(nombre)') \
                .eq('estado', 'pendiente') \
                .in_('tipo_color', ['rojo', 'amarilla', 'amarillo', 'naranja']) \
                .execute()
            
            critical_alerts = []
            
            if response.data:
                for alert in response.data:
                    resolution = self._get_alert_resolution(alert.get('titulo', ''), alert.get('tipo_color', ''))
                    
                    prod_name = alert.get('productos', {}).get('nombre') if alert.get('productos') else None
                    
                    critical_alerts.append({
                        'id': alert.get('id'),
                        'titulo': alert.get('titulo', 'Alerta sin título'),
                        'descripcion': alert.get('descripcion', ''),
                        'tipo': alert.get('tipo_color', 'warning'),
                        'producto': prod_name,
                        'resolucion': resolution,
                        'resolution': resolution  # Alias para compatibilidad
                    })
            
            logger.info(f"[ALERTAS] {len(critical_alerts)} alertas críticas detectadas")
            
            return {
                'alerts': critical_alerts,
                'total_critical': len(critical_alerts)
            }
            
        except Exception as e:
            logger.error(f"Error analizando alertas críticas: {e}")
        
        return {'alerts': [], 'total_critical': 0}
    
    def _get_alert_resolution(self, titulo: str, tipo: str) -> str:
        """Genera plan de resolución contextual según tipo de alerta."""
        titulo_lower = titulo.lower()
        
        if 'stock' in titulo_lower or 'inventario' in titulo_lower:
            return "Realizar pedido urgente al proveedor y actualizar stock mínimo"
        elif 'peso' in titulo_lower or 'excedido' in titulo_lower:
            return "Redistribuir productos en otros estantes para balancear carga"
        elif 'venta' in titulo_lower or 'ingreso' in titulo_lower:
            return "Revisar historial de transacciones y validar con comprobantes"
        elif 'usuario' in titulo_lower or 'acceso' in titulo_lower:
            return "Auditar logs de usuario y verificar permisos de acceso"
        else:
            return "Revisar dashboard de auditoría y validar datos del sistema"
    
    # ==================== AUDITORÍA ====================
    
    def analyze_audit_anomalies(self) -> Dict[str, any]:
        """Detecta usuarios con actividad sospechosa en auditoría con análisis temporal detallado."""
        try:
            # Eventos últimas 24h
            response = self.supabase.table('auditoria_eventos') \
                .select('usuario, accion, fecha, detalle') \
                .gte('fecha', (datetime.now() - timedelta(hours=24)).isoformat()) \
                .order('fecha', desc=True) \
                .execute()
            
            if response.data:
                # Contar eventos por usuario con análisis temporal
                user_activity = {}
                hourly_distribution = {}  # Distribución por hora
                
                for event in response.data:
                    user = event.get('usuario', 'Usuario desconocido')
                    accion = event.get('accion', 'Sin especificar')
                    fecha_str = event.get('fecha', '')
                    
                    if user not in user_activity:
                        user_activity[user] = {
                            'count': 0, 
                            'actions': [], 
                            'action_types': {},
                            'first_event': fecha_str,
                            'last_event': fecha_str,
                            'hourly_events': {}
                        }
                    
                    user_activity[user]['count'] += 1
                    user_activity[user]['actions'].append(accion)
                    user_activity[user]['last_event'] = fecha_str
                    
                    # Contar tipos de acción
                    user_activity[user]['action_types'][accion] = \
                        user_activity[user]['action_types'].get(accion, 0) + 1
                    
                    # Distribución horaria
                    try:
                        event_time = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                        hour = event_time.hour
                        user_activity[user]['hourly_events'][hour] = \
                            user_activity[user]['hourly_events'].get(hour, 0) + 1
                        hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
                    except:
                        pass
                
                # Calcular promedio de eventos por usuario
                avg_events_per_user = sum(u['count'] for u in user_activity.values()) / len(user_activity) if user_activity else 0
                
                # Detectar usuarios con actividad alta (>20 eventos/hora O >215% del promedio)
                suspicious_users = []
                
                for user, data in user_activity.items():
                    events_per_hour = data['count'] / 24
                    deviation_percent = ((data['count'] - avg_events_per_user) / avg_events_per_user * 100) if avg_events_per_user > 0 else 0
                    
                    # Encontrar hora pico
                    peak_hour = max(data['hourly_events'].items(), key=lambda x: x[1]) if data['hourly_events'] else (0, 0)
                    
                    if events_per_hour > 20 or deviation_percent > 215:
                        suspicious_users.append({
                            'usuario': user,
                            'total_events': data['count'],
                            'events_per_hour': round(events_per_hour, 1),
                            'deviation_percent': round(deviation_percent, 0),
                            'avg_baseline': round(avg_events_per_user, 0),
                            'action_types': data['action_types'],
                            'peak_hour': f"{peak_hour[0]:02d}:00",
                            'peak_events': peak_hour[1],
                            'first_event': data['first_event'],
                            'last_event': data['last_event'],
                            'main_actions': list(set(data['actions']))[:3]
                        })
                
                return {
                    'suspicious_users': sorted(suspicious_users, key=lambda x: x['total_events'], reverse=True),
                    'total_suspicious': len(suspicious_users),
                    'total_events': len(response.data),
                    'unique_users': len(user_activity),
                    'avg_events_per_user': round(avg_events_per_user, 0),
                    'hourly_distribution': hourly_distribution
                }
            
        except Exception as e:
            logger.error(f"Error analizando anomalías de auditoría: {e}")
        
        return {
            'suspicious_users': [], 
            'total_suspicious': 0, 
            'total_events': 0, 
            'unique_users': 0,
            'avg_events_per_user': 0,
            'hourly_distribution': {}
        }


# Instancia global
_advanced_insights: Optional[AdvancedMLInsights] = None


def get_advanced_insights() -> AdvancedMLInsights:
    """Retorna instancia singleton."""
    global _advanced_insights
    if _advanced_insights is None:
        _advanced_insights = AdvancedMLInsights()
    return _advanced_insights
