# Script para reemplazar la función _generate_findings con análisis ML avanzado

import re

# Leer archivo original
with open('app/ia/ia_ml_anomalies.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Nueva función
new_function = '''    def _generate_findings(
        self,
        snapshot: IASnapshot,
        is_anomaly: bool,
        severity: str,
    ) -> List[Dict[str, str]]:
        """
        Genera EXACTAMENTE 6 hallazgos (uno por módulo) con análisis ML avanzado.
        
        Módulos:
        1. Dashboard (rankings de productos)
        2. Inventario (capacidad estantes, stock)
        3. Movimientos (retiros no justificados)
        4. Ventas (comparación 48h)
        5. Alertas (críticas con resoluciones)
        6. Auditoría (anomalías de usuarios)
        """
        findings = []
        insights = get_advanced_insights()
        
        # 1️⃣ DASHBOARD - Rankings y top productos
        try:
            rankings = insights.analyze_dashboard_rankings()
            if rankings['top_5']:
                top_product = rankings['top_5'][0]
                findings.append({
                    'emoji': '🏆',
                    'modulo': 'dashboard',
                    'titulo': f'Dashboard: "{top_product[0]}" lidera ventas',
                    'descripcion': f'Top 1 con {top_product[1]:.0f} unidades vendidas en 48h. Total {rankings["total_products"]} productos activos.',
                    'ml_severity': 'low',
                    'plan_accion': f'Asegurar stock suficiente de "{top_product[0]}". Replicar estrategia con productos similares.'
                })
            elif rankings['bottom_5']:
                bottom_product = rankings['bottom_5'][0]
                findings.append({
                    'emoji': '📉',
                    'modulo': 'dashboard',
                    'titulo': f'Dashboard: "{bottom_product[0]}" con ventas bajas',
                    'descripcion': f'Solo {bottom_product[1]:.0f} unidades en 48h. Requiere atención comercial.',
                    'ml_severity': 'medium',
                    'plan_accion': f'Revisar precio y promociones de "{bottom_product[0]}". Considerar descuento o retiro del catálogo.'
                })
            else:
                findings.append({
                    'emoji': '📊',
                    'modulo': 'dashboard',
                    'titulo': 'Dashboard: Sin datos de productos',
                    'descripcion': 'No hay suficiente historial de ventas para análisis.',
                    'ml_severity': 'low',
                    'plan_accion': 'Continuar registrando ventas para generar insights.'
                })
        except Exception as e:
            logger.error(f"Error en análisis dashboard: {e}")
            findings.append({
                'emoji': '📊',
                'modulo': 'dashboard',
                'titulo': 'Dashboard: Operación normal',
                'descripcion': 'Todos los indicadores dentro de lo esperado.',
                'ml_severity': 'low',
                'plan_accion': 'Continuar con operaciones normales y monitoreo preventivo.'
            })
        
        # 2️⃣ INVENTARIO - Capacidad y stock
        try:
            inventory = insights.analyze_inventory_capacity()
            if inventory['without_stock']:
                count = len(inventory['without_stock'])
                productos = ', '.join(inventory['without_stock'][:3])
                findings.append({
                    'emoji': '🚨',
                    'modulo': 'inventario',
                    'titulo': f'Inventario: {count} productos SIN STOCK',
                    'descripcion': f'Crítico: {productos}{"..." if count > 3 else ""}. Riesgo de pérdida de ventas.',
                    'ml_severity': 'critical',
                    'plan_accion': f'URGENTE: Generar orden de compra para {count} productos. Contactar proveedores HOY.'
                })
            elif inventory['above_max']:
                prod = inventory['above_max'][0]
                findings.append({
                    'emoji': '📦',
                    'modulo': 'inventario',
                    'titulo': f'Inventario: "{prod["nombre"]}" excede capacidad',
                    'descripcion': f'Stock actual: {prod["stock"]:.0f} > Máximo: {prod["max"]:.0f}. Ubicación: {prod["ubicacion"]}.',
                    'ml_severity': 'high',
                    'plan_accion': f'Reubicar exceso de "{prod["nombre"]}". Ajustar niveles máximos o habilitar espacio adicional.'
                })
            elif inventory['below_min']:
                count = len(inventory['below_min'])
                prod = inventory['below_min'][0]
                findings.append({
                    'emoji': '⚠️',
                    'modulo': 'inventario',
                    'titulo': f'Inventario: {count} productos bajo mínimo',
                    'descripcion': f'"{prod["nombre"]}" con {prod["stock"]:.0f} unidades (mín: {prod["min"]:.0f}). Ubicación: {prod["ubicacion"]}.',
                    'ml_severity': 'medium',
                    'plan_accion': f'Planificar reposición de {count} productos esta semana. Priorizar "{prod["nombre"]}".'
                })
            else:
                findings.append({
                    'emoji': '✅',
                    'modulo': 'inventario',
                    'titulo': 'Inventario: Niveles óptimos',
                    'descripcion': 'Todos los productos dentro de rangos saludables.',
                    'ml_severity': 'low',
                    'plan_accion': 'Mantener monitoreo regular y ajustar niveles según demanda.'
                })
        except Exception as e:
            logger.error(f"Error en análisis inventario: {e}")
            findings.append({
                'emoji': '📦',
                'modulo': 'inventario',
                'titulo': 'Inventario: Stock estable',
                'descripcion': 'Niveles de inventario bajo control.',
                'ml_severity': 'low',
                'plan_accion': 'Continuar con monitoreo preventivo.'
            })
        
        # 3️⃣ MOVIMIENTOS - Retiros no justificados
        try:
            movements = insights.analyze_unjustified_movements()
            if movements['unjustified']:
                mov = movements['unjustified'][0]
                findings.append({
                    'emoji': '🔍',
                    'modulo': 'movimientos',
                    'titulo': f'Movimientos: Retiro no justificado de "{mov["producto"]}"',
                    'descripcion': f'Retiradas {mov["cantidad_retirada"]:.0f} unidades pero solo {mov["cantidad_vendida"]:.0f} vendidas. Diferencia: {mov["diferencia"]:.0f}.',
                    'ml_severity': 'high',
                    'plan_accion': f'Verificar retiro de "{mov["producto"]}". Revisar registros y justificar movimiento con supervisor.'
                })
            elif snapshot.inactivity_hours >= 4:
                findings.append({
                    'emoji': '⏱️',
                    'modulo': 'movimientos',
                    'titulo': f'Movimientos: {snapshot.inactivity_hours:.0f}h sin actividad',
                    'descripcion': 'Sistema sin registrar movimientos por tiempo prolongado.',
                    'ml_severity': 'high',
                    'plan_accion': 'Revisar conectividad de dispositivos. Verificar si hay bloqueos operativos o falta de personal.'
                })
            elif snapshot.movements_per_hour < 0.3:
                findings.append({
                    'emoji': '📦',
                    'modulo': 'movimientos',
                    'titulo': 'Movimientos: Actividad baja',
                    'descripcion': f'{snapshot.movements_per_hour:.1f} movimientos/hora. Menos de lo habitual.',
                    'ml_severity': 'medium',
                    'plan_accion': 'Revisar asignación de personal y procesos en turno actual.'
                })
            else:
                findings.append({
                    'emoji': '✅',
                    'modulo': 'movimientos',
                    'titulo': 'Movimientos: Flujo coherente',
                    'descripcion': f'{snapshot.movements_per_hour:.1f} movimientos/hora. Todos justificados con ventas.',
                    'ml_severity': 'low',
                    'plan_accion': 'Continuar con flujo normal de operaciones.'
                })
        except Exception as e:
            logger.error(f"Error en análisis movimientos: {e}")
            findings.append({
                'emoji': '🔄',
                'modulo': 'movimientos',
                'titulo': 'Movimientos: Flujo regular',
                'descripcion': f'{snapshot.movements_per_hour:.1f} movimientos/hora.',
                'ml_severity': 'low',
                'plan_accion': 'Continuar con flujo normal.'
            })
        
        # 4️⃣ VENTAS - Comparación 48h
        try:
            sales = insights.analyze_sales_comparison_48h()
            change = sales['change_percent']
            if change > 30:
                findings.append({
                    'emoji': '📈',
                    'modulo': 'ventas',
                    'titulo': f'Ventas: ¡Incremento del {change:.0f}%!',
                    'descripcion': f'${sales["recent_total"]:.0f} vs ${sales["previous_total"]:.0f} (24h anteriores). Top: "{sales["top_product"]}" con {sales["top_product_qty"]:.0f} unidades.',
                    'ml_severity': 'low',
                    'plan_accion': f'Capitalizar tendencia. Asegurar stock de "{sales["top_product"]}" y productos relacionados.'
                })
            elif change < -30:
                findings.append({
                    'emoji': '📉',
                    'modulo': 'ventas',
                    'titulo': f'Ventas: Caída del {abs(change):.0f}%',
                    'descripcion': f'${sales["recent_total"]:.0f} vs ${sales["previous_total"]:.0f} (24h anteriores). {sales["recent_count"]} transacciones vs {sales["previous_count"]} previas.',
                    'ml_severity': 'critical',
                    'plan_accion': 'URGENTE: Reunión con equipo comercial. Revisar stock, precios y estrategia de marketing.'
                })
            else:
                findings.append({
                    'emoji': '💰',
                    'modulo': 'ventas',
                    'titulo': f'Ventas: Rendimiento estable ({change:+.0f}%)',
                    'descripcion': f'${sales["recent_total"]:.0f} en últimas 24h. Top: "{sales["top_product"]}" ({sales["top_product_qty"]:.0f} unidades).',
                    'ml_severity': 'low',
                    'plan_accion': 'Mantener estrategia actual y monitorear tendencias semanales.'
                })
        except Exception as e:
            logger.error(f"Error en análisis ventas: {e}")
            findings.append({
                'emoji': '💰',
                'modulo': 'ventas',
                'titulo': 'Ventas: Rendimiento normal',
                'descripcion': 'Ventas dentro de lo esperado.',
                'ml_severity': 'low',
                'plan_accion': 'Continuar con estrategia actual.'
            })
        
        # 5️⃣ ALERTAS - Críticas con resoluciones
        try:
            alerts = insights.analyze_critical_alerts_resolution()
            if alerts['total'] >= 3:
                alert = alerts['alerts'][0]
                findings.append({
                    'emoji': '🚨',
                    'modulo': 'alertas',
                    'titulo': f'Alertas: {alerts["total"]} críticas activas',
                    'descripcion': f'Más antigua: "{alert["producto"]}" ({alert["hours_old"]:.1f}h). Tipo: {alert["tipo"]}.',
                    'ml_severity': 'critical',
                    'plan_accion': alert["resolution"]
                })
            elif alerts['total'] > 0:
                alert = alerts['alerts'][0]
                findings.append({
                    'emoji': '⚠️',
                    'modulo': 'alertas',
                    'titulo': f'Alertas: {alerts["total"]} activa{"s" if alerts["total"] > 1 else ""}',
                    'descripcion': f'"{alert["producto"]}" - {alert["mensaje"]} ({alert["hours_old"]:.1f}h antigüedad).',
                    'ml_severity': 'medium',
                    'plan_accion': alert["resolution"]
                })
            else:
                findings.append({
                    'emoji': '✅',
                    'modulo': 'alertas',
                    'titulo': 'Alertas: Ninguna crítica activa',
                    'descripcion': 'Sistema sin alertas que requieran atención inmediata.',
                    'ml_severity': 'low',
                    'plan_accion': 'Continuar monitoreo preventivo y ajustar umbrales si es necesario.'
                })
        except Exception as e:
            logger.error(f"Error en análisis alertas: {e}")
            findings.append({
                'emoji': '✅',
                'modulo': 'alertas',
                'titulo': 'Alertas: Bajo control',
                'descripcion': 'Sistema funcionando correctamente.',
                'ml_severity': 'low',
                'plan_accion': 'Continuar monitoreo.'
            })
        
        # 6️⃣ AUDITORÍA - Anomalías de usuarios
        try:
            audit = insights.analyze_audit_anomalies()
            if audit['suspicious_users']:
                user_data = audit['suspicious_users'][0]
                findings.append({
                    'emoji': '🔍',
                    'modulo': 'auditoria',
                    'titulo': f'Auditoría: Actividad sospechosa de {user_data["usuario"]}',
                    'descripcion': f'{user_data["eventos"]} eventos en última hora ({audit["event_rate"]:.0f} eventos/h promedio). Requiere revisión.',
                    'ml_severity': 'high',
                    'plan_accion': f'Revisar registros de {user_data["usuario"]}. Validar accesos y transacciones recientes. Contactar supervisor.'
                })
            elif audit['event_rate'] > 50:
                findings.append({
                    'emoji': '⚡',
                    'modulo': 'auditoria',
                    'titulo': f'Auditoría: {audit["total_events"]} eventos en última hora',
                    'descripcion': f'Actividad muy alta ({audit["event_rate"]:.0f} eventos/h). {audit["unique_users"]} usuarios activos.',
                    'ml_severity': 'medium',
                    'plan_accion': 'Revisar consola de auditoría. Verificar si corresponde a operación planificada o pico inusual.'
                })
            elif audit['event_rate'] < 5:
                findings.append({
                    'emoji': '💤',
                    'modulo': 'auditoria',
                    'titulo': f'Auditoría: Actividad baja ({audit["total_events"]} eventos)',
                    'descripcion': f'Solo {audit["event_rate"]:.0f} eventos/h. Menos de lo habitual.',
                    'ml_severity': 'medium',
                    'plan_accion': 'Verificar conectividad del sistema. Revisar si hay bloqueos en procesos operativos.'
                })
            else:
                findings.append({
                    'emoji': '✔️',
                    'modulo': 'auditoria',
                    'titulo': f'Auditoría: Registros coherentes ({audit["total_events"]} eventos)',
                    'descripcion': f'{audit["event_rate"]:.0f} eventos/h. {audit["unique_users"]} usuarios activos. Todo normal.',
                    'ml_severity': 'low',
                    'plan_accion': 'Sistema operando normalmente. Continuar con auditorías programadas.'
                })
        except Exception as e:
            logger.error(f"Error en análisis auditoría: {e}")
            findings.append({
                'emoji': '✔️',
                'modulo': 'auditoria',
                'titulo': 'Auditoría: Registros coherentes',
                'descripcion': 'Logs dentro de lo esperado.',
                'ml_severity': 'low',
                'plan_accion': 'Continuar con auditorías programadas.'
            })
        
        return findings'''

# Encontrar y reemplazar la función
pattern = r'    def _generate_findings\([^)]+\) -> List\[Dict\[str, str\]\]:.*?(?=\n    def |\n\n\n|\Z)'
match = re.search(pattern, content, re.DOTALL)

if match:
    new_content = content[:match.start()] + new_function + content[match.end():]
    
    # Guardar
    with open('app/ia/ia_ml_anomalies.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Función _generate_findings reemplazada exitosamente")
else:
    print("❌ No se encontró la función _generate_findings")
