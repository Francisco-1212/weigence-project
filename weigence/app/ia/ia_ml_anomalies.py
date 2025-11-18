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
        Genera hallazgos individuales para mostrar en carrusel.
        Cada hallazgo tiene: emoji, título, descripción.
        """
        if not is_anomaly:
            return [{
                'emoji': '✅',
                'title': 'Operación normal',
                'description': 'Todo funciona dentro de los parámetros esperados.'
            }]
        
        findings = []
        
        # 🚨 ALERTAS CRÍTICAS
        if snapshot.critical_alerts >= 5:
            findings.append({
                'emoji': '🚨',
                'title': f'{snapshot.critical_alerts} alertas rojas activas',
                'description': f'Hay {snapshot.critical_alerts} problemas críticos que requieren atención inmediata. Revisa la sección de alertas.'
            })
        elif snapshot.critical_alerts >= 3:
            findings.append({
                'emoji': '⚠️',
                'title': f'{snapshot.critical_alerts} alertas críticas',
                'description': f'Se detectaron {snapshot.critical_alerts} alertas rojas. Atiéndelas antes de que empeoren.'
            })
        
        # 📉 VENTAS BAJAS
        if snapshot.sales_trend_percent < -70:
            findings.append({
                'emoji': '📉',
                'title': f'Ventas cayeron {abs(snapshot.sales_trend_percent):.0f}%',
                'description': f'Las ventas están {abs(snapshot.sales_trend_percent):.0f}% más bajas que ayer. Puede ser falta de stock o problema del sistema.'
            })
        elif snapshot.sales_trend_percent < -40:
            findings.append({
                'emoji': '📊',
                'title': f'Ventas {abs(snapshot.sales_trend_percent):.0f}% más bajas',
                'description': 'Día flojo de ventas. Revisa si hay productos agotados o promociones que no están funcionando.'
            })
        
        # ⏱️ INACTIVIDAD
        if snapshot.inactivity_hours >= 4:
            findings.append({
                'emoji': '⏱️',
                'title': f'{snapshot.inactivity_hours:.0f}h sin movimientos',
                'description': f'No hay registros de actividad en las últimas {snapshot.inactivity_hours:.0f} horas. Verifica sensores y conectividad.'
            })
        elif snapshot.inactivity_hours >= 2:
            findings.append({
                'emoji': '⏰',
                'title': f'{snapshot.inactivity_hours:.0f}h de inactividad',
                'description': 'Periodo largo sin movimientos registrados. Si debería haber actividad, revisa los sensores.'
            })
        
        # 📦 MOVIMIENTOS BAJOS
        if snapshot.movements_per_hour < 0.3 and snapshot.inactivity_hours < 2:
            findings.append({
                'emoji': '📦',
                'title': 'Actividad muy baja',
                'description': f'Solo {snapshot.movements_per_hour:.1f} movimientos por hora. Ritmo muy bajo para horario normal.'
            })
        
        # ⚖️ PESO INESTABLE
        if snapshot.weight_volatility > 0.5:
            findings.append({
                'emoji': '⚖️',
                'title': 'Sensores inestables',
                'description': 'Las lecturas de peso están muy irregulares. Puede ser problema técnico o manipulación incorrecta.'
            })
        
        # Si no hay hallazgos específicos, crear uno genérico
        if not findings:
            findings.append({
                'emoji': '🔍',
                'title': 'Patrón anómalo detectado',
                'description': 'El sistema identificó un comportamiento fuera de lo normal. Revisa las métricas principales.'
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
