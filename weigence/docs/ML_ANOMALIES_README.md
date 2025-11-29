# 🤖 Detección de Anomalías con Machine Learning

Sistema de detección de anomalías **100% gratuito** usando Isolation Forest de scikit-learn.

## ✨ Características

- ✅ **Sin costo**: No requiere APIs externas (OpenAI, Claude, etc.)
- ✅ **Detección automática**: Identifica patrones anómalos en tiempo real
- ✅ **10 métricas**: Ventas, inventario, actividad, alertas
- ✅ **Severidad automática**: Low/Medium/High según el score
- ✅ **Recomendaciones**: Acciones específicas por tipo de anomalía
- ✅ **Integración transparente**: Se añade a las recomendaciones actuales

## 📦 Instalación

1. **Instalar scikit-learn:**
```bash
pip install scikit-learn==1.3.2
```

O mejor, reinstalar todas las dependencias:
```bash
pip install -r app/requirements.txt
```

## 🚀 Uso

### 1. Entrenar el modelo (PRIMERA VEZ)

```bash
python scripts/entrenar_ml_anomalies.py
```

Esto generará snapshots históricos y entrenará el modelo. **Requiere mínimo 5 días de datos** en:
- `ventas` (últimas 48-72h)
- `pesajes` (últimas 72h)  
- `movimientos_inventario` (últimas 48h)
- `alertas` (últimas 48h)

### 2. Ver resultados

El sistema ahora detecta anomalías automáticamente cuando generas recomendaciones:

```python
# En tu código Python
from app.ia import detect_anomalies
from app.ia.ia_snapshots import snapshot_builder

snapshot = snapshot_builder.build(contexto="auditoria")
insights = detect_anomalies(snapshot)

print(insights)
# {
#   'is_anomaly': True,
#   'anomaly_score': -0.487,
#   'severity': 'medium',
#   'top_contributors': [
#     ('sales_trend_percent', 0.342),
#     ('inactivity_hours', 0.289),
#     ('critical_alerts', 0.201)
#   ],
#   'recommended_actions': [
#     '🔴 Caída anómala en ventas detectada...',
#     '⏱️ Periodo de inactividad anómalo...'
#   ]
# }
```

### 3. Frontend

El frontend muestra automáticamente:
- 🤖 **Badge ML** cuando detecta anomalía
- **Panel de insights ML** con score y severidad
- **Acciones recomendadas** específicas

## 📊 Métricas Analizadas

| Métrica | Descripción | Rango Normal |
|---------|-------------|--------------|
| `sales_trend_percent` | Tendencia de ventas | -10% a +15% |
| `sales_anomaly_score` | Z-score de ventas | -1.5 a +1.5 |
| `sales_volatility` | Volatilidad de ventas | 0.05 a 0.20 |
| `weight_volatility` | Volatilidad de peso | 0.05 a 0.18 |
| `weight_change_rate` | Cambio de inventario | -8% a +5% |
| `movements_per_hour` | Actividad operativa | 0.35 a 2.5 mov/h |
| `inactivity_hours` | Horas sin actividad | 0 a 2h |
| `critical_alerts` | Alertas críticas | 0 a 1 |
| `warning_alerts` | Alertas warning | 0 a 3 |
| `signal_strength` | Señal compuesta | 0.15 a 0.60 |

## 🎯 Ejemplos de Detección

### ✅ Normal (No anomalía)
```python
{
  'is_anomaly': False,
  'anomaly_score': 0.123,
  'severity': 'low',
  'recommended_actions': ['Operación estable...']
}
```

### ⚠️ Anomalía Media
```python
{
  'is_anomaly': True,
  'anomaly_score': -0.421,
  'severity': 'medium',
  'top_contributors': [
    ('weight_volatility', 0.45),
    ('movements_per_hour', 0.32)
  ],
  'recommended_actions': [
    '⚖️ Lecturas de peso inestables...'
  ]
}
```

### 🚨 Anomalía Alta
```python
{
  'is_anomaly': True,
  'anomaly_score': -0.782,
  'severity': 'high',
  'recommended_actions': [
    '⚡ ANOMALÍA SEVERA: Requiere atención inmediata',
    '🔴 Caída anómala en ventas detectada...',
    '🚨 Acumulación crítica de alertas...'
  ]
}
```

## 🔧 Configuración Avanzada

### Cambiar sensibilidad

Edita `app/ia/ia_ml_anomalies.py`:

```python
detector = AnomalyDetector(
    contamination=0.1,  # 10% = moderado (default)
    # contamination=0.05  # 5% = estricto (menos anomalías)
    # contamination=0.15  # 15% = relajado (más anomalías)
)
```

### Re-entrenar modelo

```bash
# Con más días históricos (mejor precisión)
python scripts/entrenar_ml_anomalies.py --dias 14

# Con menos días (más rápido)
python scripts/entrenar_ml_anomalies.py --dias 5
```

## 🧪 Testing

```python
# Test manual
from app.ia.ia_ml_anomalies import get_detector
from app.ia.ia_snapshots import snapshot_builder

detector = get_detector()
snapshot = snapshot_builder.build()

is_anomaly, score, contributions = detector.predict(snapshot)
print(f"Anomalía: {is_anomaly}, Score: {score:.3f}")
```

## 📈 Próximas Mejoras

- [ ] Persistencia del modelo en base de datos
- [ ] Re-entrenamiento automático semanal
- [ ] Feedback de usuario para mejorar modelo
- [ ] Predicción de ventas con ML
- [ ] Dashboard de métricas ML

## 🐛 Troubleshooting

### "Snapshots insuficientes"
- **Causa**: No hay suficientes datos en las tablas
- **Solución**: Genera más datos operacionales o reduce `--dias`

### "Modelo no entrenado"
- **Causa**: No ejecutaste `entrenar_ml_anomalies.py`
- **Solución**: Ejecuta el script de entrenamiento

### "ImportError: sklearn"
- **Causa**: scikit-learn no instalado
- **Solución**: `pip install scikit-learn==1.3.2`

## 📚 Referencias

- [Isolation Forest Paper](https://cs.nju.edu.cn/zhouzh/zhouzh.files/publication/icdm08b.pdf)
- [Scikit-learn Docs](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)
- [Anomaly Detection Guide](https://scikit-learn.org/stable/modules/outlier_detection.html)
