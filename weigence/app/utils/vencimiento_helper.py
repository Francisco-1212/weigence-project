"""
Utilidades para manejo de fechas de elaboración y vencimiento
"""

from datetime import datetime, date, timedelta
from typing import Optional, Dict, Tuple


class VencimientoHelper:
    """Helper para cálculos relacionados con vencimiento de productos"""
    
    # Umbrales de vencimiento (en días)
    DIAS_CRITICO = 7      # Productos que vencen en 7 días o menos
    DIAS_PROXIMO = 30     # Productos que vencen en 30 días o menos
    
    @staticmethod
    def calcular_dias_hasta_vencimiento(fecha_vencimiento: str) -> Optional[int]:
        """
        Calcula los días restantes hasta el vencimiento
        
        Args:
            fecha_vencimiento: Fecha en formato ISO (YYYY-MM-DD) o datetime string
            
        Returns:
            Días hasta vencimiento (negativo si ya venció), None si fecha inválida
        """
        if not fecha_vencimiento:
            return None
            
        try:
            # Intentar parsear diferentes formatos
            if isinstance(fecha_vencimiento, str):
                # Formato ISO con timezone
                if 'T' in fecha_vencimiento:
                    fecha_dt = datetime.fromisoformat(fecha_vencimiento.replace('Z', '+00:00'))
                    fecha_venc = fecha_dt.date()
                else:
                    # Formato date simple
                    fecha_venc = datetime.strptime(fecha_vencimiento, '%Y-%m-%d').date()
            elif isinstance(fecha_vencimiento, datetime):
                fecha_venc = fecha_vencimiento.date()
            elif isinstance(fecha_vencimiento, date):
                fecha_venc = fecha_vencimiento
            else:
                return None
                
            hoy = date.today()
            dias = (fecha_venc - hoy).days
            return dias
            
        except (ValueError, AttributeError, TypeError):
            return None
    
    @staticmethod
    def obtener_estado_vencimiento(fecha_vencimiento: str) -> Dict[str, any]:
        """
        Obtiene el estado de vencimiento de un producto
        
        Args:
            fecha_vencimiento: Fecha en formato ISO
            
        Returns:
            Dict con estado, dias_restantes, nivel, color, mensaje
        """
        dias = VencimientoHelper.calcular_dias_hasta_vencimiento(fecha_vencimiento)
        
        if dias is None:
            return {
                'estado': 'sin_fecha',
                'dias_restantes': None,
                'nivel': 'info',
                'color': '#6B7280',
                'mensaje': 'Sin fecha de vencimiento'
            }
        
        if dias < 0:
            return {
                'estado': 'vencido',
                'dias_restantes': dias,
                'nivel': 'critico',
                'color': '#DC2626',
                'mensaje': 'Vencido',
                'mensaje_detallado': f'Vencido hace {abs(dias)} día(s)'
            }
        elif dias == 0:
            return {
                'estado': 'vence_hoy',
                'dias_restantes': 0,
                'nivel': 'critico',
                'color': '#DC2626',
                'mensaje': 'Vence HOY'
            }
        elif dias <= VencimientoHelper.DIAS_CRITICO:
            return {
                'estado': 'critico',
                'dias_restantes': dias,
                'nivel': 'alto',
                'color': '#EF4444',
                'mensaje': f'Vence en {dias} día(s) - CRÍTICO'
            }
        elif dias <= VencimientoHelper.DIAS_PROXIMO:
            return {
                'estado': 'proximo',
                'dias_restantes': dias,
                'nivel': 'medio',
                'color': '#F59E0B',
                'mensaje': f'Vence en {dias} día(s)'
            }
        else:
            return {
                'estado': 'vigente',
                'dias_restantes': dias,
                'nivel': 'bajo',
                'color': '#10B981',
                'mensaje': f'Vigente ({dias} día(s))'
            }
    
    @staticmethod
    def validar_fechas(fecha_elaboracion: str, fecha_vencimiento: str) -> Tuple[bool, str]:
        """
        Valida que las fechas sean coherentes
        
        Returns:
            (es_valido, mensaje_error)
        """
        if not fecha_vencimiento:
            return True, ""  # Es opcional
        
        try:
            # Parsear fechas
            if fecha_elaboracion:
                fecha_elab = datetime.strptime(fecha_elaboracion, '%Y-%m-%d').date()
            else:
                fecha_elab = None
                
            fecha_venc = datetime.strptime(fecha_vencimiento, '%Y-%m-%d').date()
            
            # Validar que vencimiento no sea en el pasado lejano (más de 5 años)
            hoy = date.today()
            if (hoy - fecha_venc).days > 1825:  # 5 años
                return False, "Fecha de vencimiento muy antigua"
            
            # Validar que elaboración sea antes de vencimiento
            if fecha_elab and fecha_elab >= fecha_venc:
                return False, "La fecha de elaboración debe ser anterior al vencimiento"
            
            # Validar que elaboración no sea en el futuro
            if fecha_elab and fecha_elab > hoy:
                return False, "La fecha de elaboración no puede ser futura"
            
            return True, ""
            
        except (ValueError, AttributeError):
            return False, "Formato de fecha inválido (usar YYYY-MM-DD)"
    
    @staticmethod
    def formatear_fecha(fecha: str, formato: str = '%d/%m/%Y') -> str:
        """
        Formatea una fecha para visualización
        
        Args:
            fecha: Fecha en formato ISO
            formato: Formato de salida (por defecto dd/mm/yyyy)
            
        Returns:
            Fecha formateada o cadena vacía si es inválida
        """
        if not fecha:
            return ""
            
        try:
            if 'T' in fecha:
                fecha_dt = datetime.fromisoformat(fecha.replace('Z', '+00:00'))
            else:
                fecha_dt = datetime.strptime(fecha, '%Y-%m-%d')
            
            return fecha_dt.strftime(formato)
        except (ValueError, AttributeError):
            return ""
    
    @staticmethod
    def debe_alertar_vencimiento(fecha_vencimiento: str) -> bool:
        """
        Determina si se debe generar una alerta por vencimiento
        
        Returns:
            True si debe alertar (vencido, vence hoy, o dentro de 7 días)
        """
        dias = VencimientoHelper.calcular_dias_hasta_vencimiento(fecha_vencimiento)
        if dias is None:
            return False
        
        # Alertar si ya venció o vence en 7 días o menos
        return dias <= VencimientoHelper.DIAS_CRITICO
