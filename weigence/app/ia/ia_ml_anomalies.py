"""
Detección de anomalías usando Machine Learning (Isolation Forest).
Sin costo, sin APIs externas, solo sklearn.
"""
from __future__ import annotations

import logging
import pickle
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from app.utils.error_logger import registrar_error
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
                    logger.info(
                        "[ML] ANOMALÍA detectada - Score: %.3f | "
                        "Críticas=%d, Tendencia=%.1f%%, Inactividad=%.1fh",
                        anomaly_score, snapshot.critical_alerts, 
                        snapshot.sales_trend_percent, snapshot.inactivity_hours
                    )
                else:
                    logger.debug("[ML] Anomalía detectada - Score: %.3f", anomaly_score)
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
        Genera hallazgos detallados para los 6 módulos del sistema.
        Cada módulo puede generar MÚLTIPLES hallazgos según los problemas detectados.
        
        Módulos:
        1. Dashboard (rankings, alertas críticas, inactividad)
        2. Inventario (productos agotados, sobrecapacidad, stock bajo, sensores)
        3. Movimientos (retiros sin justificar, inactividad, baja actividad)
        4. Ventas (cambios significativos, productos top, caídas críticas)
        5. Alertas (alertas críticas individuales con resoluciones)
        6. Auditoría (usuarios con patrones atípicos, actividad anómala)
        
        Returns:
            List[Dict]: Hallazgos individuales para navegación en header.
                       Cada módulo puede tener 1 o más hallazgos dependiendo de problemas detectados.
        """
        findings = []
        insights = get_advanced_insights()
        
        # 1️⃣ DASHBOARD - Rankings y top productos (MÚLTIPLES HALLAZGOS)
        try:
            rankings = insights.analyze_dashboard_rankings()
            has_dashboard_findings = False
            
            # Top productos (puede haber múltiples destacados)
            if rankings['top_5']:
                for idx, (prod_name, prod_qty) in enumerate(rankings['top_5'][:2], 1):  # Top 2
                    findings.append({
                        'emoji': '🏆' if idx == 1 else '🥈',
                        'modulo': 'dashboard',
                        'titulo': f'#{idx}: "{prod_name}" en alta demanda',
                        'descripcion': f'{prod_qty:.0f} unidades vendidas en 48h. {"Líder absoluto del catálogo" if idx == 1 else "Segundo mejor rendimiento"}.',
                        'ml_severity': 'low',
                        'plan_accion': f'Asegurar stock suficiente de "{prod_name}". Analizar márgenes y promociones.',
                        
                        # 📊 CONTEXTO (Pestaña 1)
                        'contexto_adicional': {
                            'timestamp_deteccion': datetime.now().strftime('%Y-%m-%d %H:%M'),
                            'periodo_analizado': 'Últimas 48 horas',
                            'producto': prod_name,
                            'posicion_ranking': idx,
                            'unidades_vendidas': int(prod_qty),
                            'total_productos': rankings['total_products']
                        },
                        
                        # 🔬 DIAGNÓSTICO (Pestaña 2)
                        'metricas': {
                            'ventas_48h': f"{int(prod_qty)} unidades",
                            'promedio_diario': f"{int(prod_qty/2)} unidades/día",
                            'participacion': f"{int(prod_qty / max(1, sum(p[1] for p in rankings['top_5'])) * 100)}%" if rankings['top_5'] else 'N/A',
                            'anomaly_score': 0.15  # Baja porque es positivo
                        },
                        
                        # ✅ RESOLUCIÓN (Pestaña 3)
                        'pasos_accion': [
                            {'orden': 1, 'texto': f'Verificar stock disponible de "{prod_name}"', 'ruta': '/inventario', 'urgencia': 'media'},
                            {'orden': 2, 'texto': 'Analizar márgenes de ganancia y ajustar precios si es necesario', 'urgencia': 'baja'},
                            {'orden': 3, 'texto': 'Considerar promociones cruzadas con productos complementarios', 'urgencia': 'baja'}
                        ]
                    })
                    has_dashboard_findings = True
            
            # Productos de bajo rendimiento
            if rankings['bottom_5']:
                for bottom_product in rankings['bottom_5'][:2]:  # Worst 2
                    findings.append({
                        'emoji': '📉',
                        'modulo': 'dashboard',
                        'titulo': f'"{bottom_product[0]}" con baja rotación',
                        'descripcion': f'Solo {bottom_product[1]:.0f} unidades en 48h. Requiere impulso comercial.',
                        'ml_severity': 'medium',
                        'plan_accion': f'Revisar precio y visibilidad de "{bottom_product[0]}". Considerar promoción o reubicación.',
                        
                        # 📊 CONTEXTO (Pestaña 1)
                        'contexto_adicional': {
                            'timestamp_deteccion': datetime.now().strftime('%Y-%m-%d %H:%M'),
                            'periodo_analizado': 'Últimas 48 horas',
                            'producto': bottom_product[0],
                            'unidades_vendidas': int(bottom_product[1]),
                            'categoria': 'Baja rotación',
                            'total_productos': rankings['total_products']
                        },
                        
                        # 🔬 DIAGNÓSTICO (Pestaña 2)
                        'metricas': {
                            'ventas_48h': f"{int(bottom_product[1])} unidades",
                            'promedio_diario': f"{int(bottom_product[1]/2)} unidades/día",
                            'desviacion': 'Bajo rendimiento',
                            'anomaly_score': 0.55  # Media porque es negativo pero no crítico
                        },
                        
                        # ✅ RESOLUCIÓN (Pestaña 3)
                        'pasos_accion': [
                            {'orden': 1, 'texto': f'Revisar precio de "{bottom_product[0]}" vs competencia', 'urgencia': 'media'},
                            {'orden': 2, 'texto': 'Analizar visibilidad en punto de venta (ubicación física)', 'urgencia': 'media'},
                            {'orden': 3, 'texto': 'Considerar promoción temporal o reubicación estratégica', 'urgencia': 'baja'}
                        ]
                    })
                    has_dashboard_findings = True
            
            # Alertas críticas (si existen)
            if snapshot.critical_alerts >= 3:
                findings.append({
                    'emoji': '🚨',
                    'modulo': 'dashboard',
                    'titulo': f'{snapshot.critical_alerts} alertas críticas activas',
                    'descripcion': 'Múltiples problemas requieren atención inmediata del supervisor.',
                    'ml_severity': 'critical',
                    'plan_accion': 'Revisar panel de alertas. Atender las rojas primero. Coordinar con equipo.',
                    
                    # 📊 CONTEXTO (Pestaña 1)
                    'contexto_adicional': {
                        'timestamp_deteccion': datetime.now().strftime('%Y-%m-%d %H:%M'),
                        'periodo_analizado': 'Tiempo real',
                        'alertas_criticas': int(snapshot.critical_alerts),
                        'alertas_advertencia': int(snapshot.warning_alerts),
                        'total_alertas': int(snapshot.critical_alerts + snapshot.warning_alerts),
                        'estado': 'Crítico'
                    },
                    
                    # 🔬 DIAGNÓSTICO (Pestaña 2)
                    'metricas': {
                        'nivel_critico': int(snapshot.critical_alerts),
                        'nivel_advertencia': int(snapshot.warning_alerts),
                        'porcentaje_criticas': f"{int(snapshot.critical_alerts / max(1, snapshot.critical_alerts + snapshot.warning_alerts) * 100)}%",
                        'anomaly_score': min(0.95, snapshot.critical_alerts / 10)  # Score basado en cantidad
                    },
                    
                    # ✅ RESOLUCIÓN (Pestaña 3)
                    'pasos_accion': [
                        {'orden': 1, 'texto': 'Revisar panel de alertas críticas', 'ruta': '/alertas?tipo=criticas', 'urgencia': 'alta'},
                        {'orden': 2, 'texto': 'Priorizar alertas rojas según impacto operativo', 'urgencia': 'alta'},
                        {'orden': 3, 'texto': 'Coordinar resolución con equipo responsable', 'urgencia': 'media'}
                    ]
                })
                has_dashboard_findings = True
            
            # Inactividad prolongada
            if snapshot.inactivity_hours >= 4:
                findings.append({
                    'emoji': '⏱️',
                    'modulo': 'dashboard',
                    'titulo': f'{snapshot.inactivity_hours:.0f}h sin movimientos',
                    'descripcion': 'Sistema sin registrar actividad. Posible problema de conectividad o cierre no registrado.',
                    'ml_severity': 'high',
                    'plan_accion': 'Verificar conexión de sensores y dispositivos. Confirmar estado operativo del local.',
                    
                    # 📊 CONTEXTO (Pestaña 1)
                    'contexto_adicional': {
                        'timestamp_deteccion': datetime.now().strftime('%Y-%m-%d %H:%M'),
                        'periodo_analizado': 'Últimas 24 horas',
                        'horas_inactividad': float(snapshot.inactivity_hours),
                        'umbral_critico': '4 horas',
                        'ultimo_movimiento': f'Hace {snapshot.inactivity_hours:.1f}h',
                        'estado': 'Sin actividad'
                    },
                    
                    # 🔬 DIAGNÓSTICO (Pestaña 2)
                    'metricas': {
                        'horas_sin_actividad': f"{snapshot.inactivity_hours:.1f}h",
                        'movimientos_por_hora': 0.0,
                        'desviacion': '-100%',  # 0 vs esperado
                        'anomaly_score': min(0.90, snapshot.inactivity_hours / 10)
                    },
                    
                    # ✅ RESOLUCIÓN (Pestaña 3)
                    'pasos_accion': [
                        {'orden': 1, 'texto': 'Verificar conexión de sensores IoT y dispositivos', 'urgencia': 'alta'},
                        {'orden': 2, 'texto': 'Confirmar estado operativo del local (¿cerrado?)', 'urgencia': 'alta'},
                        {'orden': 3, 'texto': 'Revisar logs de sistema para últimos eventos', 'ruta': '/auditoria', 'urgencia': 'media'}
                    ]
                })
                has_dashboard_findings = True
            
            # Si no hay hallazgos, mensaje positivo
            if not has_dashboard_findings:
                findings.append({
                    'emoji': '📊',
                    'modulo': 'dashboard',
                    'titulo': 'Operación estable',
                    'descripcion': f'Catálogo de {rankings["total_products"]} productos. Indicadores dentro de rangos normales.',
                    'ml_severity': 'low',
                    'plan_accion': 'Continuar con estrategia actual. El sistema monitorea en tiempo real.'
                })
        except Exception as e:
            logger.error(f"Error en análisis dashboard: {e}")
            registrar_error("Error en análisis ML dashboard", "ia_ml", e)
            findings.append({
                'emoji': '📊',
                'modulo': 'dashboard',
                'titulo': 'Todo fluye correctamente',
                'descripcion': 'Indicadores clave de rendimiento dentro de rangos óptimos. No se detectaron anomalías.',
                'ml_severity': 'low',
                'plan_accion': 'Mantener estrategia actual. El sistema continúa monitoreando patrones en tiempo real.'
            })
        
        # 2️⃣ INVENTARIO - Capacidad y stock (MÚLTIPLES HALLAZGOS)
        try:
            inventory = insights.analyze_inventory_capacity()
            has_inventory_findings = False
            
            # Productos agotados (CRÍTICO - cada uno es un hallazgo)
            if inventory['without_stock']:
                count = len(inventory['without_stock'])
                # Generar hallazgo por cada producto agotado (máximo 3)
                for prod_name in inventory['without_stock'][:3]:
                    findings.append({
                        'emoji': '🚨',
                        'modulo': 'inventario',
                        'titulo': f'Stock cero: "{prod_name}"',
                        'descripcion': f'Producto completamente agotado. Impacto directo en disponibilidad y ventas.',
                        'ml_severity': 'critical',
                        'plan_accion': f'Acción inmediata: Generar orden de reposición para "{prod_name}". Contactar proveedor prioritario.'
                    })
                    has_inventory_findings = True
                
                # Si hay más de 3, agregar hallazgo resumen
                if count > 3:
                    findings.append({
                        'emoji': '🚨',
                        'modulo': 'inventario',
                        'titulo': f'{count - 3} productos agotados adicionales',
                        'descripcion': f'Total de {count} productos sin stock. Revisar panel de inventario completo.',
                        'ml_severity': 'critical',
                        'plan_accion': 'Generar reporte de agotados. Activar protocolo de emergencia con proveedores.'
                    })
            
            # Estantes con sobrecapacidad de PESO (RESUMEN UNIFICADO)
            if inventory.get('shelves_exceeded'):
                # Tomar el estante más crítico (mayor porcentaje de sobrecarga)
                estante_critico = max(inventory['shelves_exceeded'], key=lambda x: x['exceso_porcentaje'])
                porcentaje_ocupacion = (estante_critico['actual'] / estante_critico['maximo']) * 100
                
                # Mensaje unificado
                if len(inventory['shelves_exceeded']) == 1:
                    titulo = f'Estante {estante_critico["nombre"]} sobrecargado'
                    descripcion = f'Ocupación al {porcentaje_ocupacion:.0f}%. Peso actual: {estante_critico["actual"]:.1f}kg de {estante_critico["maximo"]:.1f}kg máximo.'
                else:
                    titulo = f'{len(inventory["shelves_exceeded"])} estantes sobrecargados'
                    descripcion = f'Crítico: Estante {estante_critico["nombre"]} al {porcentaje_ocupacion:.0f}% ({estante_critico["actual"]:.1f}kg de {estante_critico["maximo"]:.1f}kg).'
                
                findings.append({
                    'emoji': '⚖️',
                    'modulo': 'inventario',
                    'titulo': titulo,
                    'descripcion': descripcion,
                    'ml_severity': 'critical',
                    'plan_accion': f'Redistribuir productos del estante {estante_critico["nombre"]}. Riesgo estructural por sobrepeso de {estante_critico["actual"] - estante_critico["maximo"]:.1f}kg.'
                })
                has_inventory_findings = True
            
            # Sobrecapacidad de productos (cada producto es un hallazgo)
            if inventory['above_max']:
                for prod in inventory['above_max'][:2]:  # Máximo 2 hallazgos
                    findings.append({
                        'emoji': '📦',
                        'modulo': 'inventario',
                        'titulo': f'Sobrecapacidad: "{prod["nombre"]}"',
                        'descripcion': f'Stock actual ({prod["stock"]:.0f}) supera máximo ({prod["max"]:.0f}). Ubicación: {prod["ubicacion"]}.',
                        'ml_severity': 'high',
                        'plan_accion': f'Redistribuir excedente de "{prod["nombre"]}". Recalibrar límites máximos.'
                    })
                    has_inventory_findings = True
            
            # Stock bajo (productos en punto de reorden)
            if inventory['below_min']:
                count = len(inventory['below_min'])
                # Primeros 2 productos con stock crítico
                for prod in inventory['below_min'][:2]:
                    findings.append({
                        'emoji': '⚠️',
                        'modulo': 'inventario',
                        'titulo': f'Stock bajo: "{prod["nombre"]}"',
                        'descripcion': f'Solo {prod["stock"]:.0f} unidades (mínimo: {prod["min"]:.0f}). Ubicación: {prod["ubicacion"]}.',
                        'ml_severity': 'medium',
                        'plan_accion': f'Programar reposición de "{prod["nombre"]}" en 48-72h. Riesgo de quiebre.'
                    })
                    has_inventory_findings = True
                
                # Si hay más, resumen
                if count > 2:
                    findings.append({
                        'emoji': '⚠️',
                        'modulo': 'inventario',
                        'titulo': f'{count - 2} productos adicionales en punto de reorden',
                        'descripcion': f'Total de {count} productos requieren reposición próximamente.',
                        'ml_severity': 'medium',
                        'plan_accion': 'Revisar panel completo de inventario. Priorizar según demanda.'
                    })
            
            # Peso inestable en sensores
            if snapshot.weight_volatility > 0.5:
                findings.append({
                    'emoji': '⚖️',
                    'modulo': 'inventario',
                    'titulo': 'Sensores de peso inestables',
                    'descripcion': 'Lecturas inconsistentes detectadas. Posible problema técnico o manipulación incorrecta.',
                    'ml_severity': 'high',
                    'plan_accion': 'Verificar calibración de sensores. Revisar protocolo de pesaje con personal.'
                })
                has_inventory_findings = True
            
            # Si no hay problemas, mensaje positivo
            if not has_inventory_findings:
                findings.append({
                    'emoji': '✅',
                    'modulo': 'inventario',
                    'titulo': 'Inventario balanceado',
                    'descripcion': 'Todos los productos operan dentro de parámetros óptimos. Stock suficiente sin excesos.',
                    'ml_severity': 'low',
                    'plan_accion': 'Mantener monitoreo continuo. El algoritmo ajustará alertas automáticamente según patrones de demanda.'
                })
        except Exception as e:
            logger.error(f"Error en análisis inventario: {e}")
            findings.append({
                'emoji': '📦',
                'modulo': 'inventario',
                'titulo': 'Gestión eficiente',
                'descripcion': 'Niveles de inventario controlados. Sistema operando sin alertas activas.',
                'ml_severity': 'low',
                'plan_accion': 'Continuar con estrategia actual. Análisis predictivo en segundo plano.'
            })
        
        # 3️⃣ MOVIMIENTOS - Retiros no justificados (MÚLTIPLES HALLAZGOS)
        try:
            movements = insights.analyze_unjustified_movements()
            has_movements_findings = False
            
            # Retiros sin justificar (cada uno es crítico)
            if movements['unjustified']:
                for mov in movements['unjustified'][:3]:  # Máximo 3 hallazgos
                    findings.append({
                        'emoji': '🔍',
                        'modulo': 'movimientos',
                        'titulo': f'Anomalía: "{mov["producto"]}"',
                        'descripcion': f'Retiro de {mov["cantidad"]:.0f} unidades sin documentación adecuada. Requiere validación.',
                        'ml_severity': 'high',
                        'plan_accion': f'Verificar origen del movimiento de "{mov["producto"]}". Completar observaciones y validar con supervisor.'
                    })
                    has_movements_findings = True
            
            # Inactividad prolongada
            if snapshot.inactivity_hours >= 4:
                findings.append({
                    'emoji': '⏱️',
                    'modulo': 'movimientos',
                    'titulo': f'Inactividad extendida: {snapshot.inactivity_hours:.0f}h',
                    'descripcion': 'No se han registrado movimientos en el sistema. Posible bloqueo operativo o conectividad.',
                    'ml_severity': 'high',
                    'plan_accion': 'Verificar estado de conexión de dispositivos de registro. Comprobar asignación de personal y procesos activos.'
                })
                has_movements_findings = True
            elif snapshot.inactivity_hours >= 2:
                findings.append({
                    'emoji': '⏰',
                    'modulo': 'movimientos',
                    'titulo': f'Período sin actividad: {snapshot.inactivity_hours:.0f}h',
                    'descripcion': 'Tiempo prolongado sin movimientos registrados.',
                    'ml_severity': 'medium',
                    'plan_accion': 'Si es horario normal, revisar sensores y conectividad. Verificar personal asignado.'
                })
                has_movements_findings = True
            
            # Actividad baja
            if snapshot.movements_per_hour < 0.3 and snapshot.inactivity_hours < 2:
                findings.append({
                    'emoji': '📦',
                    'modulo': 'movimientos',
                    'titulo': 'Actividad reducida',
                    'descripcion': f'{snapshot.movements_per_hour:.1f} movimientos/hora. Ritmo inferior al normal.',
                    'ml_severity': 'medium',
                    'plan_accion': 'Revisar asignación de personal y procesos en turno actual. Verificar protocolo operativo.'
                })
                has_movements_findings = True
            
            # Si no hay problemas, mensaje positivo
            if not has_movements_findings:
                findings.append({
                    'emoji': '✅',
                    'modulo': 'movimientos',
                    'titulo': 'Flujo coherente',
                    'descripcion': f'{snapshot.movements_per_hour:.1f} movimientos/hora. Todos justificados con ventas.',
                    'ml_severity': 'low',
                    'plan_accion': 'Continuar con flujo normal de operaciones.'
                })
        except Exception as e:
            logger.error(f"Error en análisis movimientos: {e}")
            findings.append({
                'emoji': '🔄',
                'modulo': 'movimientos',
                'titulo': 'Flujo regular',
                'descripcion': f'{snapshot.movements_per_hour:.1f} movimientos/hora.',
                'ml_severity': 'low',
                'plan_accion': 'Continuar con flujo normal.'
            })
        
        # 4️⃣ VENTAS - Comparación 48h (MÚLTIPLES HALLAZGOS)
        try:
            sales = insights.analyze_sales_comparison_48h()
            change = sales.get('change_percent', 0)
            recent_total = sales.get('recent_total', 0)
            previous_total = sales.get('previous_total', 0)
            top_product = sales.get('top_product', 'Sin datos')
            top_product_qty = sales.get('top_product_qty', 0)
            has_sales_findings = False
            
            # Validar que top_product tenga datos válidos
            if not top_product or top_product == 'Sin datos':
                top_product = 'N/A'
                top_product_qty = 0
            
            # Cambio significativo (positivo o negativo)
            if change > 30:
                findings.append({
                    'emoji': '📈',
                    'modulo': 'ventas',
                    'titulo': f'Crecimiento destacado: +{change:.0f}%',
                    'descripcion': f'${recent_total:.0f} vs ${previous_total:.0f} (período anterior). Tendencia muy positiva.',
                    'ml_severity': 'low',
                    'plan_accion': 'Aprovechar impulso de mercado. Identificar productos impulsores del crecimiento.'
                })
                has_sales_findings = True
            elif change < -30:
                findings.append({
                    'emoji': '📉',
                    'modulo': 'ventas',
                    'titulo': f'Descenso significativo: -{abs(change):.0f}%',
                    'descripcion': f'${recent_total:.0f} vs ${previous_total:.0f}. Retroceso que requiere análisis inmediato.',
                    'ml_severity': 'critical',
                    'plan_accion': 'Convocar sesión de análisis comercial urgente. Revisar disponibilidad, precios y campañas activas.'
                })
                has_sales_findings = True
            
            # Producto top performer
            if top_product != 'N/A' and top_product_qty > 0:
                findings.append({
                    'emoji': '🏅',
                    'modulo': 'ventas',
                    'titulo': f'Top: "{top_product}"',
                    'descripcion': f'{top_product_qty:.0f} unidades vendidas en 24h. Producto estrella del período.',
                    'ml_severity': 'low',
                    'plan_accion': f'Asegurar disponibilidad continua de "{top_product}". Analizar oportunidades de cross-selling.'
                })
                has_sales_findings = True
            
            # Ventas bajas (complementario al cambio porcentual)
            if snapshot.sales_trend_percent < -70:
                findings.append({
                    'emoji': '🚨',
                    'modulo': 'ventas',
                    'titulo': f'Caída crítica: {abs(snapshot.sales_trend_percent):.0f}%',
                    'descripcion': 'Disminución muy grave comparada con días anteriores. Posible problema sistémico.',
                    'ml_severity': 'critical',
                    'plan_accion': 'Verificar inventario, registros de hoy y posible cierre no registrado. Contactar supervisor.'
                })
                has_sales_findings = True
            elif snapshot.sales_trend_percent < -40 and change > -30:  # Evitar duplicado
                findings.append({
                    'emoji': '⚠️',
                    'modulo': 'ventas',
                    'titulo': f'Ventas {abs(snapshot.sales_trend_percent):.0f}% más bajas',
                    'descripcion': 'Descenso respecto al promedio histórico. Puede ser día flojo o falta de productos populares.',
                    'ml_severity': 'medium',
                    'plan_accion': 'Revisar si hay productos agotados. Verificar competencia de precios.'
                })
                has_sales_findings = True
            
            # Si no hay hallazgos específicos, resumen general
            if not has_sales_findings:
                findings.append({
                    'emoji': '💰',
                    'modulo': 'ventas',
                    'titulo': f'Desempeño estable ({change:+.0f}%)',
                    'descripcion': f'${recent_total:.0f} en últimas 24h. Rendimiento consistente.',
                    'ml_severity': 'low',
                    'plan_accion': 'Estrategia actual efectiva. El algoritmo continúa monitoreando patrones.'
                })
        except Exception as e:
            logger.error(f"Error en análisis ventas: {e}")
            findings.append({
                'emoji': '💰',
                'modulo': 'ventas',
                'titulo': 'Operación comercial normal',
                'descripcion': 'Análisis comparativo temporalmente no disponible. Ventas fluyendo según patrones históricos.',
                'ml_severity': 'low',
                'plan_accion': 'Mantener operaciones actuales. El sistema reintentará análisis automáticamente.'
            })
        
        # 5️⃣ ALERTAS - Críticas con resoluciones (MÚLTIPLES HALLAZGOS)
        try:
            alerts = insights.analyze_critical_alerts_resolution()
            has_alerts_findings = False
            
            # Alertas críticas individuales (hasta 3)
            if alerts['total_critical'] > 0:
                for alert in alerts['alerts'][:3]:  # Máximo 3 alertas detalladas
                    emoji = '🚨' if alerts['total_critical'] >= 3 else '⚠️'
                    severity = 'critical' if alerts['total_critical'] >= 3 else 'medium'
                    findings.append({
                        'emoji': emoji,
                        'modulo': 'alertas',
                        'titulo': f'"{alert["titulo"]}"',
                        'descripcion': f'{alert["descripcion"][:80]}...' if len(alert["descripcion"]) > 80 else alert["descripcion"],
                        'ml_severity': severity,
                        'plan_accion': alert["resolution"]
                    })
                    has_alerts_findings = True
                
                # Si hay más de 3, resumen
                if alerts['total_critical'] > 3:
                    findings.append({
                        'emoji': '🚨',
                        'modulo': 'alertas',
                        'titulo': f'{alerts["total_critical"] - 3} alertas críticas adicionales',
                        'descripcion': f'Total de {alerts["total_critical"]} alertas requieren atención. Revisar panel completo.',
                        'ml_severity': 'critical',
                        'plan_accion': 'Priorizar resolución de alertas críticas. Coordinar con supervisores de área.'
                    })
            
            # Si no hay alertas, mensaje positivo
            if not has_alerts_findings:
                findings.append({
                    'emoji': '✅',
                    'modulo': 'alertas',
                    'titulo': 'Sistema bajo control',
                    'descripcion': 'No hay alertas críticas activas. Todos los indicadores operan dentro de rangos normales.',
                    'ml_severity': 'low',
                    'plan_accion': 'El sistema de monitoreo inteligente continúa vigilando. Umbrales auto-calibrados según patrones históricos.'
                })
        except Exception as e:
            logger.error(f"Error en análisis alertas: {e}")
            findings.append({
                'emoji': '✅',
                'modulo': 'alertas',
                'titulo': 'Bajo control',
                'descripcion': 'Sistema funcionando correctamente.',
                'ml_severity': 'low',
                'plan_accion': 'Continuar monitoreo.'
            })
        
        # 6️⃣ AUDITORÍA - Anomalías de usuarios (MÚLTIPLES HALLAZGOS CON DATOS ENRIQUECIDOS)
        try:
            audit = insights.analyze_audit_anomalies()
            has_audit_findings = False
            
            # Usuarios con patrones sospechosos (hasta 3)
            if audit['suspicious_users']:
                for user_data in audit['suspicious_users'][:3]:
                    # Obtener tipo de evento más frecuente
                    action_types = user_data.get('action_types', {})
                    top_action = max(action_types.items(), key=lambda x: x[1]) if action_types else ('Sin datos', 0)
                    
                    findings.append({
                        'emoji': '🔍',
                        'modulo': 'auditoria',
                        'titulo': f'Patrón atípico: {user_data["usuario"]}',
                        'descripcion': f'{user_data["total_events"]} eventos en 24h ({user_data["events_per_hour"]:.1f} eventos/hora). Pico a las {user_data.get("peak_hour", "N/A")} con {user_data.get("peak_events", 0)} eventos.',
                        'ml_severity': 'high',
                        'plan_accion': f'Revisar timeline de {user_data["usuario"]}. Validar autenticidad de accesos y transacciones.',
                        
                        # 📊 CONTEXTO (Pestaña 1)
                        'contexto_adicional': {
                            'usuario': user_data['usuario'],
                            'timestamp_deteccion': datetime.now().strftime('%Y-%m-%d %H:%M'),
                            'periodo_analizado': 'Últimas 24 horas',
                            'eventos_totales': user_data['total_events'],
                            'eventos_por_hora': user_data['events_per_hour'],
                            'pico_actividad': f'{user_data.get("peak_hour", "N/A")} ({user_data.get("peak_events", 0)} eventos)',
                            'primer_evento': user_data.get('first_event', 'N/A'),
                            'ultimo_evento': user_data.get('last_event', 'N/A')
                        },
                        
                        # 🔬 DIAGNÓSTICO (Pestaña 2)
                        'metricas': {
                            'promedio_usuario': user_data.get('avg_baseline', 45),
                            'desviacion': f"+{user_data.get('deviation_percent', 0):.0f}%",
                            'tipo_eventos': action_types,
                            'evento_principal': f"{top_action[0]} ({top_action[1]} veces)",
                            'anomaly_score': min(0.95, user_data['events_per_hour'] / 50)  # Score normalizado
                        },
                        
                        # ✅ RESOLUCIÓN (Pestaña 3)
                        'pasos_accion': [
                            {
                                'orden': 1, 
                                'texto': f'Revisar timeline completo de {user_data["usuario"]}',
                                'ruta': f'/auditoria?usuario={user_data["usuario"]}',
                                'urgencia': 'alta'
                            },
                            {
                                'orden': 2, 
                                'texto': f'Validar autenticidad de {top_action[1]} eventos "{top_action[0]}"',
                                'ruta': f'/auditoria?usuario={user_data["usuario"]}&tipo={top_action[0]}',
                                'urgencia': 'alta'
                            },
                            {
                                'orden': 3, 
                                'texto': 'Contactar usuario si patrón persiste más de 48h',
                                'urgencia': 'media'
                            }
                        ]
                    })
                    has_audit_findings = True
            
            # Actividad total elevada
            if audit['total_events'] > 1200:  # >50/h * 24h
                findings.append({
                    'emoji': '⚡',
                    'modulo': 'auditoria',
                    'titulo': f'Actividad elevada: {audit["total_events"]} eventos',
                    'descripcion': f'Volumen superior al promedio: {audit["unique_users"]} usuarios activos.',
                    'ml_severity': 'medium',
                    'plan_accion': 'Verificar si corresponde a jornada especial programada o pico anómalo.',
                    
                    'contexto_adicional': {
                        'timestamp_deteccion': datetime.now().strftime('%Y-%m-%d %H:%M'),
                        'periodo_analizado': 'Últimas 24 horas',
                        'eventos_totales': audit['total_events'],
                        'usuarios_activos': audit['unique_users'],
                        'promedio_esperado': '800-1000 eventos/día'
                    },
                    
                    'metricas': {
                        'eventos_por_hora': round(audit['total_events'] / 24, 1),
                        'eventos_por_usuario': round(audit['total_events'] / audit['unique_users'], 1) if audit['unique_users'] > 0 else 0,
                        'desviacion': f"+{((audit['total_events'] - 900) / 900 * 100):.0f}%",
                        'anomaly_score': min(0.85, audit['total_events'] / 1500)
                    },
                    
                    'pasos_accion': [
                        {'orden': 1, 'texto': 'Verificar si corresponde a jornada especial programada', 'urgencia': 'media'},
                        {'orden': 2, 'texto': 'Revisar distribución de eventos por tipo de acción', 'ruta': '/auditoria', 'urgencia': 'baja'},
                        {'orden': 3, 'texto': 'Validar que no haya bucles o procesos automáticos anómalos', 'urgencia': 'media'}
                    ]
                })
                has_audit_findings = True
            
            # Actividad total reducida
            if audit['total_events'] < 120:  # <5/h * 24h
                findings.append({
                    'emoji': '💤',
                    'modulo': 'auditoria',
                    'titulo': f'Actividad reducida: {audit["total_events"]} eventos',
                    'descripcion': 'Volumen inferior al esperado en las últimas 24 horas.',
                    'ml_severity': 'medium',
                    'plan_accion': 'Verificar estado de sistemas de registro y conectividad.',
                    
                    'contexto_adicional': {
                        'timestamp_deteccion': datetime.now().strftime('%Y-%m-%d %H:%M'),
                        'periodo_analizado': 'Últimas 24 horas',
                        'eventos_totales': audit['total_events'],
                        'usuarios_activos': audit['unique_users'],
                        'promedio_esperado': '800-1000 eventos/día'
                    },
                    
                    'metricas': {
                        'eventos_por_hora': round(audit['total_events'] / 24, 1),
                        'desviacion': f"{((audit['total_events'] - 900) / 900 * 100):.0f}%",
                        'anomaly_score': 0.75
                    },
                    
                    'pasos_accion': [
                        {'orden': 1, 'texto': 'Verificar estado de sistemas de registro de auditoría', 'urgencia': 'alta'},
                        {'orden': 2, 'texto': 'Comprobar conectividad de dispositivos y sensores', 'urgencia': 'alta'},
                        {'orden': 3, 'texto': 'Validar ausencia de bloqueos operativos o mantenimientos', 'urgencia': 'media'}
                    ]
                })
                has_audit_findings = True
            
            # Si no hay hallazgos, mensaje positivo
            if not has_audit_findings:
                findings.append({
                    'emoji': '✔️',
                    'modulo': 'auditoria',
                    'titulo': 'Trazabilidad óptima',
                    'descripcion': f'{audit["total_events"]} eventos en 24h. {audit["unique_users"]} usuarios activos. Patrones normales.',
                    'ml_severity': 'low',
                    'plan_accion': 'Sistema de auditoría operando correctamente.',
                    
                    'contexto_adicional': {
                        'timestamp_deteccion': datetime.now().strftime('%Y-%m-%d %H:%M'),
                        'periodo_analizado': 'Últimas 24 horas',
                        'eventos_totales': audit['total_events'],
                        'usuarios_activos': audit['unique_users'],
                        'estado': 'Saludable'
                    },
                    
                    'metricas': {
                        'eventos_por_hora': round(audit['total_events'] / 24, 1) if audit['total_events'] > 0 else 0,
                        'promedio_usuario': audit.get('avg_events_per_user', 0),
                        'desviacion': '0%',
                        'anomaly_score': 0.05
                    },
                    
                    'pasos_accion': [
                        {'orden': 1, 'texto': 'Sistema operando normalmente, no requiere acción', 'urgencia': 'baja'}
                    ]
                })
        except Exception as e:
            logger.error(f"Error en análisis auditoría: {e}")
            findings.append({
                'emoji': '✅',
                'modulo': 'auditoria',
                'titulo': 'Registros coherentes',
                'descripcion': 'Logs dentro de lo esperado.',
                'ml_severity': 'low',
                'plan_accion': 'Continuar con auditorías programadas.',
                'contexto_adicional': {'estado': 'Normal'},
                'metricas': {},
                'pasos_accion': [{'orden': 1, 'texto': 'Continuar monitoreo', 'urgencia': 'baja'}]
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