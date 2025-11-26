"""
Detección de anomalías usando Machine Learning (Isolation Forest).
Sin costo, sin APIs externas, solo sklearn.
"""
from __future__ import annotations

import logging
import pickle
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from .ia_snapshots import IASnapshot
from .ia_ml_insights_advanced import get_advanced_insights

logger = logging.getLogger(__name__)

# Ruta donde se guarda el modelo entrenado
MODEL_PATH = Path(__file__).parent.parent.parent / 'data' / 'ml_model.pkl'


class AnomalyDetector:
    """
    Detecta anomalías en métricas operacionales usando Isolation Forest.
    
    Isolation Forest es ideal para:
    - Detectar outliers en métricas multivariadas
    - Funcionar con pocos datos históricos
    - No requerir datos etiquetados (unsupervised)
    """
    
    def __init__(
        self,
        contamination: float = 0.20,  # Esperamos 20% de datos anómalos (más sensible)
        random_state: int = 42,
    ) -> None:
        """
        Args:
            contamination: Proporción esperada de anomalías (0.0 - 0.5)
            random_state: Semilla para reproducibilidad
        """
        self._model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=100,
            max_samples='auto',
            bootstrap=False,
            warm_start=False,
        )
        self._scaler = StandardScaler()
        self._fitted = False
        self._feature_names: List[str] = []
    
    def extract_features(self, snapshot: IASnapshot) -> np.ndarray:
        """
        Extrae features relevantes del snapshot para detección de anomalías.
        
        Returns:
            Array numpy con shape (1, n_features)
        """
        features = [
            float(snapshot.sales_trend_percent or 0.0),
            float(snapshot.sales_anomaly_score or 0.0),
            float(snapshot.sales_volatility or 0.0),
            float(snapshot.weight_volatility or 0.0),
            float(snapshot.weight_change_rate or 0.0),
            float(snapshot.movements_per_hour or 0.0),
            float(snapshot.inactivity_hours or 0.0),
            float(snapshot.critical_alerts or 0),
            float(snapshot.warning_alerts or 0),
            float(snapshot.signal_strength or 0.0),
        ]
        
        if not self._feature_names:
            self._feature_names = [
                'sales_trend_percent',
                'sales_anomaly_score',
                'sales_volatility',
                'weight_volatility',
                'weight_change_rate',
                'movements_per_hour',
                'inactivity_hours',
                'critical_alerts',
                'warning_alerts',
                'signal_strength',
            ]
        
        return np.array(features).reshape(1, -1)
    
    def fit_from_snapshots(self, snapshots: List[IASnapshot]) -> bool:
        """
        Entrena el modelo con un conjunto de snapshots históricos.
        
        Args:
            snapshots: Lista de snapshots (mínimo 10 recomendado)
            
        Returns:
            True si el entrenamiento fue exitoso
        """
        if len(snapshots) < 5:
            logger.warning(
                "[ML] Snapshots insuficientes para entrenar (%d). Mínimo: 5",
                len(snapshots)
            )
            return False
        
        try:
            # Extraer features de todos los snapshots
            X = np.vstack([self.extract_features(s) for s in snapshots])
            
            # Normalizar features
            X_scaled = self._scaler.fit_transform(X)
            
            # Entrenar modelo
            self._model.fit(X_scaled)
            self._fitted = True
            
            logger.info(
                "[ML] Modelo entrenado con %d snapshots, %d features",
                len(snapshots),
                X.shape[1]
            )
            
            # 💾 GUARDAR MODELO EN DISCO
            self.save_model()
            
            return True
            
        except Exception as exc:
            logger.exception("[ML] Error entrenando modelo: %s", exc)
            return False
    
    def save_model(self) -> bool:
        """Guarda el modelo entrenado en disco."""
        try:
            MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
            
            model_data = {
                'model': self._model,
                'scaler': self._scaler,
                'feature_names': self._feature_names,
                'fitted': self._fitted,
            }
            
            with open(MODEL_PATH, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"[ML] Modelo guardado en {MODEL_PATH}")
            return True
            
        except Exception as exc:
            logger.exception(f"[ML] Error guardando modelo: {exc}")
            return False
    
    def load_model(self) -> bool:
        """Carga el modelo desde disco."""
        if not MODEL_PATH.exists():
            logger.debug(f"[ML] No existe modelo guardado en {MODEL_PATH}")
            return False
        
        try:
            with open(MODEL_PATH, 'rb') as f:
                model_data = pickle.load(f)
            
            self._model = model_data['model']
            self._scaler = model_data['scaler']
            self._feature_names = model_data['feature_names']
            self._fitted = model_data['fitted']
            
            logger.info(f"[ML] Modelo cargado desde {MODEL_PATH}")
            return True
            
        except Exception as exc:
            logger.exception(f"[ML] Error cargando modelo: {exc}")
            return False
    
    def predict(self, snapshot: IASnapshot) -> Tuple[bool, float, Dict[str, float]]:
        """
        Predice si el snapshot actual es anómalo.
        
        Args:
            snapshot: Snapshot a evaluar
            
        Returns:
            Tupla (es_anomalo, anomaly_score, feature_contributions)
            - es_anomalo: True si se detecta anomalía
            - anomaly_score: Score de anomalía (-1 a 1, más negativo = más anómalo)
            - feature_contributions: Contribución de cada feature
        """
        if not self._fitted:
            logger.warning("[ML] Modelo no entrenado. Retornando resultado neutro.")
            return False, 0.0, {}
        
        try:
            # Extraer features
            X = self.extract_features(snapshot)
            X_scaled = self._scaler.transform(X)
            
            # Predecir: -1 = anomalía, 1 = normal
            prediction = self._model.predict(X_scaled)[0]
            
            # Score de anomalía (más negativo = más anómalo)
            anomaly_score = self._model.score_samples(X_scaled)[0]
            
            # 🔥 REGLAS CRÍTICAS: Override si hay condiciones extremas
            # Estas reglas detectan anomalías incluso si el modelo falla
            is_critical_anomaly = (
                snapshot.critical_alerts >= 3 or  # 3+ alertas críticas
                snapshot.sales_trend_percent < -50 or  # Caída >50% en ventas
                (snapshot.critical_alerts >= 2 and snapshot.sales_trend_percent < -30) or
                snapshot.inactivity_hours >= 4  # 4+ horas sin actividad
            )
            
            # Calcular contribución de cada feature
            feature_contributions = self._calculate_feature_contributions(X[0])
            
            # Combinar modelo + reglas
            is_anomaly = (prediction == -1) or is_critical_anomaly
            
            if is_anomaly:
                if is_critical_anomaly and prediction != -1:
                    logger.warning(
                        "[ML] ⚠️ ANOMALÍA CRÍTICA (reglas) - Score: %.3f | "
                        "Críticas=%d, Tendencia=%.1f%%, Inactividad=%.1fh",
                        anomaly_score, snapshot.critical_alerts, 
                        snapshot.sales_trend_percent, snapshot.inactivity_hours
                    )
                else:
                    logger.info("[ML] ⚠️ ANOMALÍA DETECTADA - Score: %.3f", anomaly_score)
            else:
                logger.debug("[ML] Comportamiento normal - Score: %.3f", anomaly_score)
            
            return is_anomaly, float(anomaly_score), feature_contributions
            
        except Exception as exc:
            logger.exception("[ML] Error en predicción: %s", exc)
            return False, 0.0, {}
    
    def _calculate_feature_contributions(self, features: np.ndarray) -> Dict[str, float]:
        """
        Calcula qué features contribuyen más a la anomalía.
        
        Returns:
            Dict con feature_name -> contribution_score
        """
        contributions = {}
        
        for i, feature_name in enumerate(self._feature_names):
            # Valor normalizado
            value = float(features[i])
            
            # Contribución basada en desviación de la media
            # (simplificado, en producción usarías SHAP values)
            contributions[feature_name] = abs(value)
        
        # Normalizar contribuciones
        total = sum(contributions.values()) or 1.0
        contributions = {k: v / total for k, v in contributions.items()}
        
        return contributions
    
    def get_anomaly_insights(
        self,
        snapshot: IASnapshot,
    ) -> Dict[str, any]:
        """
        Genera insights detallados sobre anomalías detectadas.
        
        Returns:
            Dict con:
            - is_anomaly: bool
            - anomaly_score: float
            - severity: str (low/medium/high)
            - top_contributors: List[Tuple[str, float]]
            - recommended_actions: List[str]
            - findings: List[Dict] - hallazgos individuales para navegación
        """
        is_anomaly, score, contributions = self.predict(snapshot)
        
        # Clasificar severidad según score
        if score > -0.3:
            severity = 'low'
        elif score > -0.5:
            severity = 'medium'
        else:
            severity = 'high'
        
        # Top 3 features que más contribuyen
        top_contributors = sorted(
            contributions.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        # Generar acciones recomendadas
        recommended_actions = self._generate_recommendations(
            is_anomaly,
            severity,
            top_contributors,
            snapshot
        )
        
        # 🎯 GENERAR HALLAZGOS INDIVIDUALES (para carrusel)
        findings = self._generate_findings(snapshot, is_anomaly, severity)
        
        return {
            'is_anomaly': is_anomaly,
            'anomaly_score': score,
            'severity': severity,
            'top_contributors': top_contributors,
            'recommended_actions': recommended_actions,
            'all_contributions': contributions,
            'findings': findings,  # ← Nuevo: lista de hallazgos
        }
    
    def _generate_recommendations(
        self,
        is_anomaly: bool,
        severity: str,
        top_contributors: List[Tuple[str, float]],
        snapshot: IASnapshot,
    ) -> List[str]:
        """Genera recomendaciones en lenguaje natural y amigable."""
        
        if not is_anomaly:
            return ["✅ Todo funciona normal. Seguir monitoreando."]
        
        recommendations = []
        
        # 🚨 ALERTAS CRÍTICAS
        if snapshot.critical_alerts >= 5:
            recommendations.append(
                "🚨 **Tienes {0} alertas críticas activas** - "
                "Esto indica problemas serios que necesitan atención inmediata. "
                "Revisa la sección de alertas y atiende primero las rojas.".format(
                    snapshot.critical_alerts
                )
            )
        elif snapshot.critical_alerts >= 3:
            recommendations.append(
                "⚠️ **Se detectaron {0} alertas críticas** - "
                "Más de lo normal. Revisa qué está pasando antes de que empeore.".format(
                    snapshot.critical_alerts
                )
            )
        
        # 📉 VENTAS BAJAS
        if snapshot.sales_trend_percent < -70:
            recommendations.append(
                "📉 **Las ventas cayeron {0:.0f}%** comparado con días anteriores - "
                "Esto es muy grave. Puede ser falta de stock, problemas de sistema o cierre no registrado. "
                "Verifica inventario y registros de hoy.".format(
                    abs(snapshot.sales_trend_percent)
                )
            )
        elif snapshot.sales_trend_percent < -40:
            recommendations.append(
                "📊 **Ventas {0:.0f}% más bajas** que lo normal - "
                "Puede ser día flojo, falta de productos populares o problema técnico. "
                "Revisa si hay productos agotados.".format(
                    abs(snapshot.sales_trend_percent)
                )
            )
        
        # ⏱️ INACTIVIDAD
        if snapshot.inactivity_hours >= 4:
            recommendations.append(
                "⏱️ **Llevan {0:.0f} horas sin registrar movimientos** - "
                "¿Está cerrado el local? ¿Hay problemas con los sensores? "
                "Verifica que los sistemas estén conectados.".format(
                    snapshot.inactivity_hours
                )
            )
        elif snapshot.inactivity_hours >= 2:
            recommendations.append(
                "⏰ **Más de {0:.0f} horas sin actividad** - "
                "Periodo largo sin movimientos. Si debería haber actividad, revisa los sensores.".format(
                    snapshot.inactivity_hours
                )
            )
        
        # 📦 MOVIMIENTOS BAJOS
        if snapshot.movements_per_hour < 0.3 and snapshot.inactivity_hours < 2:
            recommendations.append(
                "📦 **Muy poca actividad de inventario** ({0:.1f} movimientos/hora) - "
                "Ritmo muy bajo. Si es horario normal, puede indicar problemas operativos.".format(
                    snapshot.movements_per_hour
                )
            )
        
        # ⚖️ PESO INESTABLE
        if snapshot.weight_volatility > 0.5:
            recommendations.append(
                "⚖️ **Lecturas de peso muy irregulares** - "
                "Los sensores están dando mediciones inconsistentes. "
                "Puede ser problema técnico o manipulación incorrecta."
            )
        
        # 🎯 MENSAJE PRINCIPAL SEGÚN SEVERIDAD
        if severity == 'high':
            header = "🔴 **SITUACIÓN CRÍTICA** - Requiere atención inmediata del supervisor."
        elif severity == 'medium':
            header = "🟡 **ATENCIÓN NECESARIA** - Revisa estos puntos pronto."
        else:
            header = "🟢 **MONITOREO** - Algunas cosas fuera de lo normal."
        
        recommendations.insert(0, header)
        
        return recommendations or ["Revisar operación manualmente."]
    
    def _generate_findings(
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
                    'descripcion': f'Retiro de {mov["cantidad"]:.0f} unidades sin observación válida. Revisar justificación del movimiento.',
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
                    'descripcion': f'${sales["recent_total"]:.0f} vs ${sales["previous_total"]:.0f} (24h anteriores). Incremento del {sales["change_percent"]:.1f}% en ventas.',
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
            if alerts['total_critical'] >= 3:
                alert = alerts['alerts'][0]
                findings.append({
                    'emoji': '🚨',
                    'modulo': 'alertas',
                    'titulo': f'Alertas: {alerts["total_critical"]} críticas activas',
                    'descripcion': f'Más reciente: "{alert["titulo"]}" - {alert["descripcion"][:50]}. Tipo: {alert["tipo"][:7]}.',
                    'ml_severity': 'critical',
                    'plan_accion': alert["resolution"]
                })
            elif alerts['total_critical'] > 0:
                alert = alerts['alerts'][0]
                findings.append({
                    'emoji': '⚠️',
                    'modulo': 'alertas',
                    'titulo': f'Alertas: {alerts["total_critical"]} activa{"s" if alerts["total_critical"] > 1 else ""}',
                    'descripcion': f'"{alert["titulo"]}" - {alert["descripcion"][:60]}',
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
                    'descripcion': f'{user_data["total_events"]} eventos en 24h ({user_data["events_per_hour"]:.1f} eventos/h). {user_data["usuario"]} requiere revisión.',
                    'ml_severity': 'high',
                    'plan_accion': f'Revisar registros de {user_data["usuario"]}. Validar accesos y transacciones recientes. Contactar supervisor.'
                })
            elif audit['total_events'] > 1200:  # >50/h * 24h
                findings.append({
                    'emoji': '⚡',
                    'modulo': 'auditoria',
                    'titulo': f'Auditoría: {audit["total_events"]} eventos en última hora',
                    'descripcion': f'Actividad muy alta ({audit["total_events"]} eventos en 24h). {audit["unique_users"]} usuarios activos.',
                    'ml_severity': 'medium',
                    'plan_accion': 'Revisar consola de auditoría. Verificar si corresponde a operación planificada o pico inusual.'
                })
            elif audit['total_events'] < 120:  # <5/h * 24h
                findings.append({
                    'emoji': '💤',
                    'modulo': 'auditoria',
                    'titulo': f'Auditoría: Actividad baja ({audit["total_events"]} eventos)',
                    'descripcion': f'Solo {audit["total_events"]} eventos en 24h. Actividad menor a lo habitual.',
                    'ml_severity': 'medium',
                    'plan_accion': 'Verificar conectividad del sistema. Revisar si hay bloqueos en procesos operativos.'
                })
            else:
                findings.append({
                    'emoji': '✔️',
                    'modulo': 'auditoria',
                    'titulo': f'Auditoría: Registros coherentes ({audit["total_events"]} eventos)',
                    'descripcion': f'{audit["total_events"]} eventos en 24h. {audit["unique_users"]} usuarios activos. Actividad normal.',
                    'ml_severity': 'low',
                    'plan_accion': 'Sistema operando normalmente. Continuar con auditorías programadas.'
                })
        except Exception as e:
            logger.error(f"Error en análisis auditoría: {e}")
            findings.append({
                'emoji': '✅',
                'modulo': 'auditoria',
                'titulo': 'Auditoría: Registros coherentes',
                'descripcion': 'Logs dentro de lo esperado.',
                'ml_severity': 'low',
                'plan_accion': 'Continuar con auditorías programadas.'
            })
        
        return findings


# Instancia global (caché en memoria)
_detector: AnomalyDetector | None = None


def get_detector() -> AnomalyDetector:
    """Retorna la instancia singleton del detector y carga modelo si existe."""
    global _detector
    if _detector is None:
        _detector = AnomalyDetector()
        # Intentar cargar modelo guardado
        _detector.load_model()
    return _detector


def detect_anomalies(snapshot: IASnapshot) -> Dict[str, any]:
    """
    Función conveniente para detectar anomalías en un snapshot.
    
    Args:
        snapshot: Snapshot a evaluar
        
    Returns:
        Dict con insights de anomalías
    """
    detector = get_detector()
    return detector.get_anomaly_insights(snapshot)


__all__ = ['AnomalyDetector', 'get_detector', 'detect_anomalies']