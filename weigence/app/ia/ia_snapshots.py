"""Snapshot builder that aggregates recent operational data."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from statistics import mean, pstdev
from typing import Any, Dict, Iterable, List, Optional

from .ia_repository import IARepository, repository
from .ia_snapshot_utils import snapshot_to_dict


def _default_alerts() -> Dict[str, int]:
    return {"critical": 0, "warning": 0, "info": 0}


def _parse_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return datetime.utcnow()
    return datetime.utcnow()


def _coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _coerce_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _coerce_optional_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _coerce_list(values: Any) -> List[float]:
    if isinstance(values, (list, tuple)):
        return [_coerce_float(item, 0.0) for item in values]
    if values is None:
        return []
    return [_coerce_float(values, 0.0)]


def _coerce_patterns(values: Any) -> List[str]:
    if isinstance(values, (list, tuple)):
        return [str(item) for item in values if item is not None]
    if values is None:
        return []
    return [str(values)]


@dataclass
class IASnapshot:
    """Aggregated metrics that describe the operational context."""

    generated_at: datetime = field(default_factory=datetime.utcnow)
    sales_window_hours: int = 0
    weight_window_hours: int = 0
    movement_window_hours: int = 0
    sales_totals: List[float] = field(default_factory=list)
    sales_trend_percent: float = 0.0
    sales_anomaly_score: float = 0.0
    sales_volatility: float = 0.0
    last_sale_total: Optional[float] = None
    baseline_sale: Optional[float] = None
    weight_values: List[float] = field(default_factory=list)
    weight_volatility: float = 0.0
    weight_change_rate: float = 0.0
    last_weight: Optional[float] = None
    alerts_summary: Dict[str, int] = field(default_factory=_default_alerts)
    movements_per_hour: float = 0.0
    inactivity_hours: float = 0.0
    pattern_flags: List[str] = field(default_factory=list)
    signal_strength: float = 0.0
    
    # Métricas adicionales para mensajes accionables
    total_productos: int = 0
    productos_sin_stock: int = 0
    ventas_ultimas_24h: int = 0
    movimientos_no_justificados: int = 0
    usuarios_sospechosos: int = 0
    audit_events_count: int = 0
    estantes_sobrecargados: int = 0
    productos_no_encontrados_movimientos: int = 0
    tiempo_ultimo_movimiento: float = 0.0  # Horas desde el último movimiento

    def __post_init__(self) -> None:
        self.alerts_summary = {
            "critical": _coerce_int(self.alerts_summary.get("critical")),
            "warning": _coerce_int(self.alerts_summary.get("warning")),
            "info": _coerce_int(self.alerts_summary.get("info")),
        }

    @property
    def critical_alerts(self) -> int:
        return self.alerts_summary.get("critical", 0)

    @property
    def warning_alerts(self) -> int:
        return self.alerts_summary.get("warning", 0)

    @property
    def info_alerts(self) -> int:
        return self.alerts_summary.get("info", 0)

    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary."""

        return snapshot_to_dict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IASnapshot":
        """Create a sanitized snapshot from raw dictionaries."""

        snapshot = cls()
        snapshot.generated_at = _parse_datetime(data.get("generated_at"))
        snapshot.sales_window_hours = _coerce_int(data.get("sales_window_hours"))
        snapshot.weight_window_hours = _coerce_int(data.get("weight_window_hours"))
        snapshot.movement_window_hours = _coerce_int(data.get("movement_window_hours"))
        snapshot.sales_totals = _coerce_list(data.get("sales_totals"))
        snapshot.sales_trend_percent = _coerce_float(data.get("sales_trend_percent"))
        snapshot.sales_anomaly_score = _coerce_float(data.get("sales_anomaly_score"))
        snapshot.sales_volatility = _coerce_float(data.get("sales_volatility"))
        snapshot.last_sale_total = _coerce_optional_float(data.get("last_sale_total"))
        snapshot.baseline_sale = _coerce_optional_float(data.get("baseline_sale"))
        snapshot.weight_values = _coerce_list(data.get("weight_values"))
        snapshot.weight_volatility = _coerce_float(data.get("weight_volatility"))
        snapshot.weight_change_rate = _coerce_float(data.get("weight_change_rate"))
        snapshot.last_weight = _coerce_optional_float(data.get("last_weight"))

        alerts_summary = data.get("alerts_summary")
        if isinstance(alerts_summary, dict):
            snapshot.alerts_summary = {
                "critical": _coerce_int(alerts_summary.get("critical")),
                "warning": _coerce_int(alerts_summary.get("warning")),
                "info": _coerce_int(alerts_summary.get("info")),
            }
        else:
            snapshot.alerts_summary = {
                "critical": _coerce_int(data.get("critical_alerts")),
                "warning": _coerce_int(data.get("warning_alerts")),
                "info": _coerce_int(data.get("info_alerts")),
            }

        snapshot.movements_per_hour = _coerce_float(data.get("movements_per_hour"))
        snapshot.inactivity_hours = _coerce_float(data.get("inactivity_hours"))
        snapshot.pattern_flags = _coerce_patterns(data.get("pattern_flags"))
        snapshot.signal_strength = _coerce_float(data.get("signal_strength"))
        
        # Métricas adicionales para mensajes accionables
        snapshot.total_productos = _coerce_int(data.get("total_productos", 0))
        snapshot.productos_sin_stock = _coerce_int(data.get("productos_sin_stock", 0))
        snapshot.ventas_ultimas_24h = _coerce_int(data.get("ventas_ultimas_24h", 0))
        snapshot.movimientos_no_justificados = _coerce_int(data.get("movimientos_no_justificados", 0))
        snapshot.usuarios_sospechosos = _coerce_int(data.get("usuarios_sospechosos", 0))
        snapshot.audit_events_count = _coerce_int(data.get("audit_events_count", 0))
        snapshot.estantes_sobrecargados = _coerce_int(data.get("estantes_sobrecargados", 0))
        snapshot.productos_no_encontrados_movimientos = _coerce_int(data.get("productos_no_encontrados_movimientos", 0))
        snapshot.tiempo_ultimo_movimiento = _coerce_float(data.get("tiempo_ultimo_movimiento", 0.0))
        
        return snapshot

    def merge(self, extra: Dict[str, Any] | None) -> "IASnapshot":
        """Return a new snapshot merging current data with the provided values."""

        if not extra:
            return IASnapshot.from_dict(self.to_dict())
        merged = {**self.to_dict(), **extra}
        return IASnapshot.from_dict(merged)


class SnapshotBuilder:
    """Coordinates data extraction and transformation into an IASnapshot."""

    def __init__(self, repo: IARepository | None = None) -> None:
        self._repo = repo or repository

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def build(self, contexto: str | None = None) -> IASnapshot:
        ahora = datetime.utcnow()
        sales_window = 48 if contexto != "inventario" else 72
        weight_window = 24
        movement_window = 24
        print(f"[DEBUG BUILD] Construyendo snapshot para contexto: {contexto}, ventana movimientos: {movement_window}h")

        ventas = self._repo.obtener_ventas_desde(ahora - timedelta(hours=sales_window))
        detalles = self._repo.obtener_detalle_ventas_desde(ahora - timedelta(hours=sales_window))
        pesajes = self._repo.obtener_pesajes_desde(ahora - timedelta(hours=weight_window))
        alertas = self._repo.obtener_alertas_desde(ahora - timedelta(hours=movement_window))
        movimientos = self._repo.obtener_movimientos_desde(ahora - timedelta(hours=movement_window))

        snapshot = IASnapshot(
            generated_at=ahora,
            sales_window_hours=sales_window,
            weight_window_hours=weight_window,
            movement_window_hours=movement_window,
        )

        self._enriquecer_ventas(snapshot, ventas)
        self._enriquecer_pesajes(snapshot, pesajes)
        self._enriquecer_alertas(snapshot, alertas)
        self._enriquecer_movimientos(snapshot, movimientos)
        self._enriquecer_metricas_adicionales(snapshot, ventas, pesajes, alertas, movimientos, detalles)
        self._inferir_patrones(snapshot, detalles)

        return snapshot
    
    def _enriquecer_metricas_adicionales(
        self,
        snapshot: IASnapshot,
        ventas: List[Dict[str, object]],
        pesajes: List[Dict[str, object]],
        alertas: List[Dict[str, object]],
        movimientos: List[Dict[str, object]],
        detalles: List[Dict[str, object]]
    ) -> None:
        """Calcula métricas adicionales para mensajes accionables del header."""
        # Total de productos únicos
        productos_unicos = set()
        for pesaje in pesajes:
            if pesaje.get('idproducto'):
                productos_unicos.add(pesaje.get('idproducto'))
        for detalle in detalles:
            if detalle.get('idproducto'):
                productos_unicos.add(detalle.get('idproducto'))
        snapshot.total_productos = len(productos_unicos) if productos_unicos else 0
        
        # Productos sin stock (peso = 0 o stock = 0)
        productos_sin_stock = sum(
            1 for pesaje in pesajes 
            if float(pesaje.get('peso_unitario', 0)) == 0 or int(pesaje.get('stock', 0)) == 0
        )
        snapshot.productos_sin_stock = productos_sin_stock
        
        # Ventas en las últimas 24 horas
        ahora = datetime.utcnow()
        hace_24h = ahora - timedelta(hours=24)
        ventas_24h = [
            v for v in ventas 
            if self._parse_fecha_venta(v.get('fecha_venta', ahora)) >= hace_24h
        ]
        snapshot.ventas_ultimas_24h = len(ventas_24h)
        
        # Eventos de auditoría (aproximado por movimientos + alertas)
        snapshot.audit_events_count = len(movimientos) + len(alertas)
        
        # Usuarios con actividad sospechosa (múltiples ajustes manuales en poco tiempo)
        # Por ahora lo dejamos en 0, se puede calcular con datos de auditoría
        snapshot.usuarios_sospechosos = 0
        
        # Calcular estantes sobrecargados
        try:
            from api.conexion_supabase import supabase
            estantes_response = supabase.table('estantes').select('id_estante, peso_actual, peso_maximo').execute()
            if estantes_response.data:
                estantes_sobrecargados = sum(
                    1 for est in estantes_response.data
                    if est.get('peso_actual', 0) > est.get('peso_maximo', float('inf'))
                )
                snapshot.estantes_sobrecargados = estantes_sobrecargados
            else:
                snapshot.estantes_sobrecargados = 0
        except Exception:
            snapshot.estantes_sobrecargados = 0
        
        # Contar productos no encontrados y calcular tiempo desde último movimiento
        print(f"[DEBUG] 🔍 Iniciando cálculo de productos no encontrados y tiempo último movimiento...")
        try:
            from api.conexion_supabase import supabase
            # Obtener todos los movimientos recientes para analizar
            mov_response = supabase.table('movimientos_inventario') \
                .select('id_movimiento, idproducto, tipo_evento, timestamp, productos(nombre)') \
                .order('timestamp', desc=True) \
                .limit(100) \
                .execute()
            
            print(f"[DEBUG] 📦 Movimientos obtenidos: {len(mov_response.data) if mov_response.data else 0}")
            
            if mov_response.data:
                # Contar movimientos donde el producto no existe (JOIN falla)
                productos_no_encontrados = 0
                for mov in mov_response.data:
                    if mov.get('productos') is None:
                        productos_no_encontrados += 1
                        print(f"[DEBUG] Producto no encontrado - ID mov: {mov.get('id_movimiento')}, idproducto: {mov.get('idproducto')}, tipo_evento: {mov.get('tipo_evento')}")
                
                snapshot.productos_no_encontrados_movimientos = productos_no_encontrados
                print(f"[DEBUG] ✅ Total productos no encontrados: {productos_no_encontrados}")
                
                # Calcular tiempo desde el último movimiento
                ultimo_movimiento = mov_response.data[0]  # Ya está ordenado desc
                timestamp_str = ultimo_movimiento.get('timestamp')
                if timestamp_str:
                    try:
                        from datetime import timezone
                        # Parsear el timestamp de Supabase
                        timestamp_dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        # Usar UTC para ambos
                        ahora_utc = datetime.now(timezone.utc)
                        tiempo_transcurrido = (ahora_utc - timestamp_dt).total_seconds() / 3600.0
                        snapshot.tiempo_ultimo_movimiento = tiempo_transcurrido
                        print(f"[DEBUG] ⏱️ Último movimiento: {timestamp_str}")
                        print(f"[DEBUG] ⏱️ Ahora UTC: {ahora_utc.isoformat()}")
                        print(f"[DEBUG] ⏱️ Diferencia: {tiempo_transcurrido:.2f} horas ({tiempo_transcurrido * 60:.1f} minutos)")
                    except Exception as e:
                        print(f"[ERROR] Error al parsear timestamp: {e}")
                        import traceback
                        traceback.print_exc()
                        snapshot.tiempo_ultimo_movimiento = 0.0
                else:
                    snapshot.tiempo_ultimo_movimiento = 0.0
            else:
                snapshot.productos_no_encontrados_movimientos = 0
                snapshot.tiempo_ultimo_movimiento = 999.0  # Sin movimientos
                print(f"[DEBUG] ⚠️ No hay datos de movimientos")
        except Exception as e:
            print(f"[ERROR] ❌ Al contar productos no encontrados: {e}")
            import traceback
            traceback.print_exc()
            snapshot.productos_no_encontrados_movimientos = 0
            snapshot.tiempo_ultimo_movimiento = 0.0
    
    def _parse_fecha_venta(self, fecha: Any) -> datetime:
        """Parse fecha de venta a datetime."""
        if isinstance(fecha, datetime):
            return fecha
        if isinstance(fecha, str):
            try:
                return datetime.fromisoformat(fecha.replace("Z", "+00:00"))
            except ValueError:
                return datetime.utcnow()
        return datetime.utcnow()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _ordenar_por_fecha(self, items: Iterable[Dict[str, object]], campo: str) -> List[Dict[str, object]]:
        def _parse(item: Dict[str, object]) -> datetime:
            valor = item.get(campo)
            if isinstance(valor, datetime):
                return valor
            if isinstance(valor, str):
                try:
                    return datetime.fromisoformat(valor.replace("Z", "+00:00"))
                except ValueError:
                    return datetime.utcnow()
            return datetime.utcnow()

        return sorted(items, key=_parse)

    def _enriquecer_ventas(self, snapshot: IASnapshot, ventas: List[Dict[str, object]]) -> None:
        if not ventas:
            snapshot.sales_totals = []
            snapshot.sales_volatility = 0.0
            snapshot.sales_anomaly_score = 0.0
            snapshot.sales_trend_percent = 0.0
            return

        ordenadas = self._ordenar_por_fecha(ventas, "fecha_venta")
        totales = [float(item.get("total") or 0.0) for item in ordenadas]
        snapshot.sales_totals = totales
        snapshot.last_sale_total = totales[-1] if totales else None
        snapshot.baseline_sale = mean(totales[:-1]) if len(totales) > 1 else (totales[0] if totales else None)

        if len(totales) > 1:
            snapshot.sales_volatility = self._calcular_volatilidad(totales)
            snapshot.sales_anomaly_score = self._calcular_z_score(totales)
            snapshot.sales_trend_percent = self._calcular_tendencia(totales)
        else:
            snapshot.sales_volatility = 0.0
            snapshot.sales_anomaly_score = 0.0
            snapshot.sales_trend_percent = 0.0

    def _enriquecer_pesajes(self, snapshot: IASnapshot, pesajes: List[Dict[str, object]]) -> None:
        if not pesajes:
            snapshot.weight_values = []
            snapshot.weight_volatility = 0.0
            snapshot.weight_change_rate = 0.0
            return

        ordenadas = self._ordenar_por_fecha(pesajes, "fecha_pesaje")
        valores = [float(item.get("peso_unitario") or 0.0) for item in ordenadas]
        snapshot.weight_values = valores
        snapshot.last_weight = valores[-1] if valores else None

        if len(valores) > 1:
            snapshot.weight_volatility = self._calcular_volatilidad(valores)
            snapshot.weight_change_rate = self._calcular_cambio_relativo(valores)
        else:
            snapshot.weight_volatility = 0.0
            snapshot.weight_change_rate = 0.0

    def _enriquecer_alertas(self, snapshot: IASnapshot, alertas: List[Dict[str, object]]) -> None:
        resumen = _default_alerts()
        for alerta in alertas:
            clave = (alerta.get("tipo_color") or "").lower()
            if "rojo" in clave or "crit" in clave:
                resumen["critical"] += 1
            elif "amar" in clave or "warn" in clave or "amarill" in clave:
                resumen["warning"] += 1
            else:
                resumen["info"] += 1
        
        snapshot.alerts_summary = resumen
        print(f"[DEBUG ALERTAS] Total alertas pendientes: {len(alertas)}, Críticas: {resumen['critical']}, Advertencias: {resumen['warning']}, Info: {resumen['info']}")

    def _enriquecer_movimientos(self, snapshot: IASnapshot, movimientos: List[Dict[str, object]]) -> None:
        if movimientos:
            intervalo_horas = snapshot.movement_window_hours or 1
            snapshot.movements_per_hour = len(movimientos) / intervalo_horas
            print(f"[DEBUG MOVIMIENTOS] Total movimientos: {len(movimientos)}, Intervalo: {intervalo_horas}h, Por hora: {snapshot.movements_per_hour}")
            ordenadas = self._ordenar_por_fecha(movimientos, "timestamp")
            ultimo = ordenadas[-1]
            ultima_fecha = ultimo.get("timestamp")
            if isinstance(ultima_fecha, str):
                try:
                    ultima_fecha_dt = datetime.fromisoformat(ultima_fecha.replace("Z", "+00:00"))
                except ValueError:
                    ultima_fecha_dt = snapshot.generated_at
            elif isinstance(ultima_fecha, datetime):
                ultima_fecha_dt = ultima_fecha
            else:
                ultima_fecha_dt = snapshot.generated_at
            snapshot.inactivity_hours = max(
                0.0,
                (snapshot.generated_at - ultima_fecha_dt).total_seconds() / 3600.0,
            )
            
            # Contar movimientos sin justificación (ajustes manuales sin motivo)
            movimientos_no_justificados = sum(
                1 for mov in movimientos 
                if mov.get('tipo') == 'ajuste_manual' and not mov.get('motivo')
            )
            snapshot.movimientos_no_justificados = movimientos_no_justificados
            
            # Contar movimientos de productos no encontrados
            # Nota: Se necesita hacer JOIN con productos para detectar esto
            # Por ahora lo dejamos en 0 y se calculará en _enriquecer_metricas_adicionales
            snapshot.productos_no_encontrados_movimientos = 0
        else:
            snapshot.movements_per_hour = 0.0
            snapshot.inactivity_hours = float(snapshot.movement_window_hours)
            snapshot.movimientos_no_justificados = 0
            print(f"[DEBUG MOVIMIENTOS] No hay movimientos en la ventana de tiempo")

    def _inferir_patrones(
        self,
        snapshot: IASnapshot,
        detalles: List[Dict[str, object]],
    ) -> None:
        patrones: List[str] = []
        if snapshot.sales_trend_percent <= -0.2:
            patrones.append("sales_drop")
        if snapshot.sales_anomaly_score <= -1.8:
            patrones.append("sudden_collapse")
        if snapshot.weight_change_rate <= -0.12:
            patrones.append("inventory_loss")
        if snapshot.weight_volatility >= 0.22:
            patrones.append("weight_instability")
        if snapshot.movements_per_hour <= 0.25:
            patrones.append("low_activity")
        if snapshot.inactivity_hours >= 3:
            patrones.append("extended_inactivity")
        if snapshot.critical_alerts >= 2:
            patrones.append("alert_pressure")
        if snapshot.sales_trend_percent >= 0.15 and snapshot.weight_change_rate >= 0.05:
            patrones.append("positive_recovery")

        # Analizamos velocidad de venta de productos para detectar patrones complementarios
        top_items = self._productos_con_mayor_variacion(detalles)
        if top_items and top_items[0][1] > 0:
            patrones.append("fast_moving_items")

        snapshot.pattern_flags = patrones
        snapshot.signal_strength = min(
            1.0,
            abs(snapshot.sales_trend_percent) * 1.5
            + abs(snapshot.weight_change_rate) * 1.3
            + snapshot.critical_alerts * 0.2,
        )

    # ------------------------------------------------------------------
    # Numeric utilities
    # ------------------------------------------------------------------
    def _calcular_volatilidad(self, valores: List[float]) -> float:
        if not valores:
            return 0.0
        promedio = mean(valores)
        if promedio == 0:
            return 0.0
        if len(valores) == 1:
            return 0.0
        return pstdev(valores) / abs(promedio)

    def _calcular_z_score(self, valores: List[float]) -> float:
        if len(valores) < 2:
            return 0.0
        promedio = mean(valores[:-1]) if len(valores) > 2 else mean(valores)
        desviacion = pstdev(valores)
        if desviacion == 0:
            return 0.0
        ultimo = valores[-1]
        return (ultimo - promedio) / desviacion

    def _calcular_tendencia(self, valores: List[float]) -> float:
        if len(valores) < 3:
            return 0.0
        tercio = max(1, len(valores) // 3)
        recientes = valores[-tercio:]
        anteriores = valores[:tercio]
        if not anteriores:
            return 0.0
        prom_reciente = mean(recientes)
        prom_anterior = mean(anteriores)
        if prom_anterior == 0:
            return 0.0
        return (prom_reciente - prom_anterior) / abs(prom_anterior)

    def _calcular_cambio_relativo(self, valores: List[float]) -> float:
        if len(valores) < 3:
            return 0.0
        recientes = valores[-3:]
        anteriores = valores[:3]
        prom_reciente = mean(recientes)
        prom_anterior = mean(anteriores)
        if prom_anterior == 0:
            return 0.0
        return (prom_reciente - prom_anterior) / abs(prom_anterior)

    def _productos_con_mayor_variacion(
        self,
        detalles: List[Dict[str, object]],
    ) -> List[tuple[str, float]]:
        conteo: Dict[str, float] = {}
        for item in detalles:
            producto = str(item.get("idproducto"))
            cantidad = float(item.get("cantidad") or 0.0)
            conteo[producto] = conteo.get(producto, 0.0) + cantidad
        ordenado = sorted(conteo.items(), key=lambda x: x[1], reverse=True)
        return ordenado[:5]


snapshot_builder = SnapshotBuilder()
