# BORRADOR DE TESIS - SISTEMA WEIGENCE

## Introducción

El presente documento constituye el marco de trabajo para el desarrollo de **Weigence**, un sistema integral de gestión de inventario basado en tecnología IoT (Internet of Things), orientado a pequeñas y medianas empresas (PYMEs) que operan centros de bodegaje y almacenamiento en diversos sectores industriales y comerciales.

**Weigence** es una solución tecnológica adaptable diseñada con arquitectura modular que permite su implementación en múltiples contextos operativos: farmacias, distribuidoras comerciales, bodegas de repuestos, almacenes de alimentos, centros logísticos de e-commerce, y cualquier PYME que requiera control preciso de inventario en tiempo real.

Si bien la plataforma posee capacidad de adaptación transversal a diferentes industrias, **el presente proyecto establecerá su caso de demostración y validación en el sector farmacéutico**. Esta elección estratégica obedece a que el sector farmacéutico presenta la mayor complejidad operativa y requisitos regulatorios más estrictos (trazabilidad ISP, control de vencimientos, gestión de lotes, normativas sanitarias). Si el sistema funciona exitosamente bajo estas exigencias máximas, garantiza su aplicabilidad en sectores con menores restricciones normativas.

Este proyecto surge como respuesta a las deficiencias operativas identificadas en la gestión tradicional de inventarios en PYMEs, proponiendo una solución que integra:
- **Sensores IoT** (balanzas inteligentes para control de peso en tiempo real)
- **Análisis de datos** (dashboards y reportes automatizados)
- **Inteligencia artificial** (detección de anomalías, recomendaciones predictivas)
- **Arquitectura web escalable** (acceso desde cualquier dispositivo)

---

## 1. Identificación del Problema

### 1.1 Actualización y justificación del problema

#### 1.1.1. Descripción de la organización

El contexto operativo de este proyecto abarca **pequeñas y medianas empresas (PYMEs) que operan centros de bodegaje y almacenamiento en Chile**, independientemente de su sector industrial. Estas organizaciones comparten características estructurales y operativas comunes que las hacen candidatas ideales para la implementación de Weigence:

**Características Transversales de las PYMEs Objetivo:**

1. **Limitaciones de capital tecnológico**: Presupuestos restringidos que dificultan la inversión en sistemas ERP (Enterprise Resource Planning) empresariales de alto costo como SAP, Oracle o Microsoft Dynamics, cuyos costos de licenciamiento e implementación superan los USD $50,000.

2. **Volumen de inventario medio**: Gestión de entre 50 y 5,000 SKUs (Stock Keeping Units) con valores de inventario totales entre $10 millones y $500 millones CLP. Este rango es suficientemente significativo para justificar la automatización, pero insuficiente para acceder a soluciones enterprise de gran escala.

3. **Infraestructura física limitada**: Espacios de almacenamiento típicos de 50m² a 500m², que requieren optimización del uso vertical de estanterías y control preciso de capacidades de carga por restricciones de espacio y presupuesto.

4. **Estructura organizacional reducida**: Equipos operativos de 3 a 15 personas con roles multifuncionales (bodegueros, supervisores, administrativos, vendedores), lo que demanda sistemas intuitivos de rápida adopción que no requieran especialistas TI dedicados.

5. **Necesidad de escalabilidad progresiva**: Empresas en fase de crecimiento que requieren soluciones modulares capaces de expandirse sin inversiones disruptivas ni migraciones complejas.

**Sectores de Aplicación:**

Weigence está diseñado para ser implementado en PYMEs de múltiples sectores:

- **Farmacias y distribuidoras farmacéuticas** (caso de demostración del proyecto)
- **Retail y comercio electrónico** (centros de fulfillment, mini-bodegas urbanas)
- **Repuestos industriales y automotrices** (distribuidoras, talleres especializados)
- **Insumos de construcción** (ferreterías, distribuidoras de materiales)
- **Alimentos y bebidas** (distribuidoras de perecibles, bodegas de abarrotes)
- **Productos electrónicos y tecnológicos** (importadoras, distribuidoras especializadas)
- **Insumos agrícolas** (distribuidoras de semillas, fertilizantes, agroquímicos)

**Caso de Demostración: Sector Farmacéutico**

Para efectos de validación y demostración del sistema, el proyecto se implementará específicamente en una **farmacia independiente o bodega de distribución farmacéutica**. La elección de este sector como caso piloto obedece a ventajas estratégicas:

- **Complejidad regulatoria máxima**: Cumplimiento obligatorio de normativas del ISP (Instituto de Salud Pública) que exigen trazabilidad completa de productos, control de lotes, fechas de vencimiento, condiciones de almacenamiento y registros de auditoría. **Si el sistema funciona bajo estas exigencias, garantiza su aplicabilidad en sectores menos regulados.**

- **Criticidad operativa**: La disponibilidad continua de medicamentos es esencial para la salud pública, lo que valida la confiabilidad y disponibilidad del sistema en entornos de alta responsabilidad y cero tolerancia a errores.

- **Diversidad de inventario**: Gestión simultánea de productos de alta rotación (analgésicos, antigripales) y baja rotación (medicamentos especializados), diferentes requisitos de temperatura (productos refrigerados vs. ambiente), y fechas de caducidad variables. Este escenario prueba la versatilidad del sistema.

- **Impacto social medible**: Mejoras en disponibilidad de medicamentos, reducción de dispensación de productos vencidos y optimización de stock tienen impacto directo y cuantificable en la comunidad.

- **Datos enriquecidos**: El sector farmacéutico genera datos de alta calidad (códigos únicos, precios regulados, clasificaciones terapéuticas) que facilitan la demostración de capacidades analíticas avanzadas del sistema.

**Adaptabilidad Post-Demostración:**

Una vez validado en el exigente entorno farmacéutico, Weigence puede ser implementado en otros sectores con ajustes menores de configuración (eliminación de controles de vencimiento obligatorios, simplificación de trazabilidad, adaptación de alertas), aprovechando el núcleo tecnológico común: sensores de peso, dashboards en tiempo real, detección de anomalías mediante IA, y gestión de usuarios con control de acceso.

#### 1.1.2. Descripción del problema

La gestión de inventarios en PYMEs presenta deficiencias sistémicas que trascienden sectores específicos y comprometen tanto la eficiencia operativa como la calidad del servicio. El análisis del estado actual revela problemáticas recurrentes independientes de la industria:

**A. Ausencia de datos en tiempo real**

Los sistemas tradicionales basados en registros manuales (cuadernos físicos, planillas Excel) o software básico de punto de venta generan **brechas temporales críticas** entre los eventos físicos (entradas, salidas, ventas, devoluciones) y su registro en el sistema. Esta latencia informativa produce:

- **Desconocimiento del stock real**: Los tomadores de decisiones trabajan con información desactualizada (horas o días de retraso), imposibilitando la gestión proactiva de reabastecimientos.

- **Detección tardía de discrepancias**: Las diferencias entre inventario físico y contable solo se descubren durante tomas de inventario periódicas (mensuales/trimestrales), cuando ya se han acumulado pérdidas significativas.

- **Incapacidad para alertas automáticas**: Sin monitoreo continuo, el sistema no puede generar notificaciones de reabastecimiento basadas en consumo real, llevando a políticas reactivas de compra.

- **Falta de visibilidad de ubicación**: En bodegas con múltiples estanterías, no existe registro preciso de la ubicación física de productos, generando tiempos de búsqueda prolongados y errores de picking.

- **Imposibilidad de análisis en tiempo real**: Los gerentes y supervisores no pueden evaluar el estado del negocio en el momento presente, retrasando respuestas a problemas emergentes.

**B. Errores derivados de procesos manuales**

La dependencia de intervención humana en cada transacción de inventario introduce múltiples puntos de fallo que impactan la integridad de los datos:

- **Errores de transcripción**: Digitación incorrecta de cantidades (confusión entre 10 y 100 unidades), códigos de producto (mezcla de SKUs similares), o fechas críticas (vencimientos, lotes de producción).

- **Omisiones de registro**: Movimientos de inventario no documentados por olvido durante períodos de alta demanda, cambios de turno, o simple sobrecarga de trabajo del personal operativo.

- **Inconsistencias de formato**: Falta de estandarización en nomenclatura de productos (mismo producto registrado con diferentes nombres), categorías solapadas, y unidades de medida inconsistentes (cajas vs. unidades individuales).

- **Retrasos en actualización**: Acumulación de registros pendientes ("lo anoto después") que obsoletan la información disponible en el sistema, haciendo inútil cualquier consulta de stock actual.

- **Dobles contabilizaciones**: Registro duplicado del mismo movimiento por diferentes usuarios o sistemas no integrados (software de ventas vs. sistema de bodega).

**C. Deficiencias en control de calidad y trazabilidad**

La gestión manual dificulta el cumplimiento de estándares operativos y regulatorios (particularmente crítico en sectores regulados como farmacéutico y alimentos):

- **Control insuficiente de fechas críticas**: En productos perecibles (medicamentos, alimentos, cosméticos), la falta de alertas automatizadas resulta en pérdidas por productos caducados antes de su venta. En el sector farmacéutico, esto representa un riesgo sanitario adicional.

- **Trazabilidad incompleta**: Imposibilidad de rastrear el recorrido completo de un producto desde su ingreso hasta su salida, dificultando respuestas efectivas ante retiros de mercado (recalls), reclamos de clientes, o auditorías regulatorias.

- **Incapacidad para implementar FIFO sistemático**: El principio "First In, First Out" (primero en entrar, primero en salir) queda a criterio del bodeguero, sin validación automática, generando rotación deficiente de stock antiguo.

- **Auditorías reactivas**: La falta de logs automáticos de transacciones impide auditorías preventivas, detectando problemas solo cuando ya han escalado a pérdidas significativas.

- **Gestión deficiente de lotes**: En industrias con productos loteados (farmacéuticos, alimentos procesados, químicos), la asociación manual de lotes a movimientos es propensa a errores que comprometen trazabilidad regulatoria.

**D. Limitaciones para análisis y toma de decisiones**

La ausencia de datos estructurados, históricos y análisis automatizados impide la gestión estratégica del inventario:

- **Desconocimiento de patrones de consumo**: Sin análisis histórico, es imposible identificar estacionalidad (productos de mayor demanda en invierno vs. verano), tendencias de crecimiento/decrecimiento, o correlaciones entre productos.

- **Detección tardía de anomalías**: Situaciones anómalas como hurtos progresivos, mermas sistemáticas, errores recurrentes de registro, o patrones inusuales de consumo pasan desapercibidas hasta generar pérdidas acumuladas.

- **Proyección de demanda empírica**: Las decisiones de compra se basan en intuición o reglas simples ("siempre pedimos X unidades"), sin aprovechar datos históricos para proyecciones estadísticas más precisas.

- **Optimización manual de niveles de stock**: La definición de puntos de reorden, stock de seguridad, y niveles máximos se hace por estimación, sin análisis cuantitativo de variabilidad de demanda ni costos de quiebre de stock.

- **Imposibilidad de análisis ABC**: Sin datos de rotación y valor, no se puede clasificar productos en categorías (A: alta rotación/alto valor, B: rotación media, C: baja rotación) para optimizar estrategias de gestión diferenciadas.

**E. Sobrecarga operativa del personal**

El tiempo invertido en tareas administrativas manuales de control de inventario genera costos de oportunidad significativos:

- **Reducción de tiempo productivo**: Horas invertidas en conteos físicos, búsquedas de productos, reconciliación de discrepancias y llenado de planillas restan tiempo a actividades de valor agregado como atención al cliente, merchandising, o desarrollo de negocio.

- **Fatiga operativa**: La repetitividad y baja estimulación de tareas administrativas genera desmotivación y errores por fatiga cognitiva, especialmente en turnos largos.

- **Limitación de escalabilidad**: El crecimiento del negocio (más SKUs, más transacciones, más clientes) requiere contratación proporcional de personal administrativo para tareas repetitivas, limitando la rentabilidad marginal de la expansión.

- **Falta de foco estratégico**: Gerentes y supervisores invierten tiempo en resolver problemas operativos rutinarios (¿dónde está el producto X? ¿cuánto stock tenemos de Y?) en lugar de dedicarse a planificación estratégica y mejora continua.

**Impacto Transversal en Diferentes Sectores:**

Si bien estos problemas son comunes a todas las PYMEs de bodegaje, su manifestación varía según sector:

- **Farmacias**: Riesgo sanitario por productos vencidos, incumplimiento normativo ISP, pérdida de confianza del paciente.
- **E-commerce**: Cancelaciones de pedidos por stock fantasma, sobreventa, insatisfacción de clientes, daño reputacional en plataformas.
- **Repuestos**: Paradas de servicio al no encontrar repuestos que sí están en bodega, pérdida de clientes industriales por falta de confiabilidad.
- **Alimentos**: Mermas por caducidad, riesgo de intoxicaciones alimentarias, sanciones del SEREMI de Salud.
- **Retail**: Oportunidades de venta perdidas en temporadas altas, sobrestock en productos de baja rotación inmovilizando capital.

La **convergencia de estos cinco bloques de problemáticas** justifica la necesidad de una solución tecnológica integral que aborde sistemáticamente cada deficiencia mediante automatización IoT, análisis de datos en tiempo real, e inteligencia artificial.

### 1.2 Justificación del problema

#### 1.1.3. Relevancia del problema

La problemática identificada trasciende la mera ineficiencia administrativa, generando **impactos económicos, operativos y estratégicos cuantificables** que afectan directamente la viabilidad y competitividad de las PYMEs:

**Impacto Económico Directo**

1. **Pérdidas por quiebres de stock (stock-outs)**: 

   La incapacidad de mantener visibilidad en tiempo real del inventario genera situaciones de desabastecimiento no planificado. Estudios del sector retail chileno indican que las PYMEs experimentan pérdidas de ventas del **5-8% anual** debido a stock-outs evitables. Para una PYME con facturación de $200M CLP/año, esto representa **$10M-$16M CLP** en ventas perdidas.

   - **Caso farmacéutico**: Un paciente que no encuentra su medicamento en una farmacia rara vez vuelve; la venta se pierde permanentemente y el cliente migra a la competencia.
   - **Caso e-commerce**: Cancelaciones de pedidos por stock fantasma (producto marcado como disponible pero físicamente agotado) generan reembolsos, costos logísticos desperdiciados, y daño reputacional en marketplaces.
   - **Caso repuestos**: Talleres mecánicos que no obtienen un repuesto urgente cambian de proveedor, perdiendo relaciones comerciales de largo plazo.

2. **Mermas por caducidad y obsolescencia**:

   Sin sistemas automatizados de alerta de vencimiento, el porcentaje de productos que alcanzan su fecha de caducidad antes de ser vendidos puede alcanzar el **2-3% del inventario total** en sectores con productos perecibles. Para una bodega farmacéutica con inventario valorizado en $100M CLP, esto representa **$2M-$3M CLP/año** en pérdidas netas.

   - **Farmacéutico**: Medicamentos vencidos deben ser destruidos con costo adicional de gestión de residuos peligrosos.
   - **Alimentos**: Productos vencidos implican pérdida total (no hay mercado secundario) más riesgo de sanciones sanitarias.
   - **Electrónica/Tecnología**: Obsolescencia tecnológica (productos que quedan desactualizados) genera depreciación acelerada del inventario.

3. **Costos de inventario excesivo (overstock)**:

   La falta de datos históricos para proyección de demanda lleva a políticas conservadoras de sobre-stock para evitar quiebres. Esto inmoviliza capital de trabajo y genera costos ocultos:

   - **Costo de oportunidad del capital**: Dinero inmovilizado en inventario excesivo podría invertirse en marketing, expansión, o instrumentos financieros. Con tasa de costo de oportunidad del **15-20% anual**, $50M CLP en overstock representan $7.5M-$10M CLP/año en costos implícitos.
   - **Costos de almacenamiento**: Arriendo de bodegas, servicios básicos, seguros, y depreciación de infraestructura. En Santiago, el costo de bodegaje ronda **$8,000-$12,000 CLP/m²/mes**.
   - **Riesgo de obsolescencia**: A mayor tiempo de permanencia en bodega, mayor riesgo de que productos se vuelvan invendibles (cambios de temporada, actualizaciones de versión, cambios regulatorios).

4. **Tiempo operativo desperdiciado**:

   Estudios de eficiencia operacional indican que bodegueros en PYMEs sin sistemas automatizados invierten **15-25% de su jornada** en tareas administrativas manuales (conteos, búsquedas, registros, reconciliaciones). Para un equipo de 5 personas con costo laboral promedio de $600,000 CLP/mes/persona:

   - Costo anual del equipo: $36M CLP
   - Tiempo desperdiciado (20%): **$7.2M CLP/año** en salarios pagados por tareas no productivas

   Este tiempo podría redirigirse a actividades de mayor valor: atención al cliente, merchandising, capacitaciones, mejora de procesos.

**Impacto Operativo**

1. **Cumplimiento regulatorio y riesgo de sanciones**:

   - **Sector Farmacéutico**: El ISP (Instituto de Salud Pública) fiscaliza trazabilidad de medicamentos. Multas por incumplimiento van desde **10 UTM ($600,000 CLP) hasta 1,000 UTM ($60M CLP)** según gravedad. En casos extremos, puede resultar en cierre temporal del establecimiento.
   
   - **Sector Alimentos**: SEREMI de Salud sanciona deficiencias en control de fechas de vencimiento y trazabilidad. Multas típicas: 5-100 UTM ($300,000 - $6M CLP).
   
   - **Comercio Exterior**: Importadoras deben mantener registros de trazabilidad para Aduana y SII. Inconsistencias pueden generar auditorías extensas con costos legales y contables asociados.

2. **Calidad de servicio y satisfacción del cliente**:

   - **Tiempos de atención prolongados**: Búsquedas manuales de productos en bodega generan esperas de 5-15 minutos por cliente, reduciendo throughput (clientes atendidos por hora) y generando abandono de compra.
   
   - **Errores en despacho**: Confusión de productos similares (falta de validación automática) genera devoluciones, reclamos, y costos de logística inversa.
   
   - **Percepción de profesionalismo**: Clientes B2B (empresas, instituciones) valoran proveedores con sistemas de gestión profesionales. Empresas que operan con planillas manuales proyectan imagen de informalidad.

3. **Escalabilidad limitada**:

   - **Techo operativo**: Procesos manuales establecen un límite máximo de transacciones procesables sin degradación de calidad. Crecer implica contratar proporcionalmente más personal administrativo, reduciendo márgenes.
   
   - **Complejidad no lineal**: Duplicar el número de SKUs más que duplica la complejidad de gestión manual (más combinaciones de productos, más tiempo de búsqueda, más errores potenciales).
   
   - **Barreras a expansión territorial**: Abrir una segunda bodega o sucursal requiere duplicar procesos manuales sin economías de escala, a diferencia de sistemas centralizados que escalan a costo marginal bajo.

**Impacto en Caso Farmacéutico (Sector de Demostración)**

Adicionalmente a los impactos económicos y operativos transversales, el sector farmacéutico presenta dimensiones críticas adicionales:

1. **Continuidad de tratamientos médicos**: 

   Desabastecimientos de medicamentos de uso crónico (antihipertensivos, anticoagulantes, insulinas, antirretrovirales) pueden interrumpir tratamientos con consecuencias graves:
   - Descompensaciones médicas que requieren hospitalización
   - Pérdida de adherencia terapéutica (pacientes que abandonan tratamiento al no encontrar medicamento)
   - Complicaciones de salud con costos sociales y económicos elevados

2. **Seguridad del paciente**:

   - **Dispensación de productos vencidos**: Riesgo directo de reducción de eficacia terapéutica o incluso toxicidad (algunos medicamentos degradados generan metabolitos tóxicos).
   
   - **Trazabilidad ante recalls**: Cuando laboratorios retiran lotes defectuosos del mercado, farmacias sin trazabilidad automatizada no pueden identificar rápidamente si dispensaron productos afectados, impidiendo notificación a pacientes en riesgo.
   
   - **Control de medicamentos controlados**: Psicotrópicos y estupefacientes requieren trazabilidad estricta. Discrepancias pueden interpretarse como desvío ilegal con implicancias penales.

**Aplicabilidad Transversal a Otros Sectores**

Los impactos económicos y operativos descritos son equivalentes (con variaciones de magnitud) en otros sectores objetivo de Weigence:

| Sector | Stock-Outs | Mermas/Caducidad | Overstock | Regulatorio |
|--------|-----------|------------------|-----------|-------------|
| **Farmacia** | 5-8% ventas perdidas | 2-3% inventario | Alto (medicamentos caros) | Crítico (ISP) |
| **E-commerce** | 10-15% cancelaciones | Bajo | Medio | Bajo |
| **Repuestos** | 8-12% ventas perdidas | Bajo (no perecen) | Alto (capital inmovilizado) | Medio (garantías) |
| **Alimentos** | 6-10% ventas perdidas | 5-8% inventario | Medio | Alto (SEREMI) |
| **Retail general** | 5-10% ventas perdidas | 1-3% (según rubro) | Alto (temporadas) | Bajo |

**Conclusión sobre Relevancia**

La convergencia de:
- **Pérdidas económicas directas** (stock-outs + mermas + costos de inventario) que típicamente alcanzan **8-15% de la facturación anual** en PYMEs sin sistemas automatizados
- **Riesgos regulatorios** con multas potenciales de magnitud significativa
- **Limitaciones de escalabilidad** que restringen el crecimiento del negocio
- **Impactos sociales** (especialmente en sectores como salud y alimentos)

Justifica la necesidad de una solución tecnológica accesible que transforme la gestión de inventarios de un **proceso reactivo y propenso a errores** a uno **proactivo, automatizado y basado en datos**, independientemente del sector de aplicación.

#### 1.1.4. Complejidad del problema

La resolución efectiva de la problemática planteada presenta **desafíos técnicos, operacionales y organizacionales significativos** que requieren una aproximación multidisciplinaria y que justifican por qué las PYMEs no pueden resolver estos problemas con soluciones simplistas:

**Desafíos Tecnológicos**

1. **Integración Hardware-Software en tiempo real**:

   La implementación de sensores IoT (balanzas inteligentes, sensores de presencia, lectores RFID) requiere resolver problemas técnicos complejos:

   - **Protocolos de comunicación robustos**: Los sensores deben transmitir datos continuamente con latencia mínima (<2 segundos) pero consumiendo poca energía. Tecnologías como MQTT, WebSockets, o protocolo HTTP/2 Server-Sent Events deben configurarse para balancear tiempo real vs. eficiencia.

   - **Sincronización multi-dispositivo**: En una bodega con 10-50 estanterías monitorizadas, el sistema debe consolidar datos de múltiples sensores simultáneos sin pérdida de información ni colisiones de datos.

   - **Manejo de conectividad intermitente**: Bodegas pueden tener zonas con cobertura WiFi deficiente. El sistema debe implementar colas de mensajes (queueing), almacenamiento local temporal (edge computing), y sincronización automática al recuperar conectividad.

   - **Calibración y precisión de sensores**: Balanzas digitales pierden calibración con el tiempo, temperatura, vibraciones. El sistema debe detectar desviaciones (comparando con registros históricos) y alertar necesidad de recalibración sin intervención manual constante.

   - **Heterogeneidad de hardware**: Weigence debe funcionar con diferentes marcas/modelos de balanzas (soporte multi-vendor) sin requerir rediseño por cada tipo de sensor.

2. **Procesamiento de datos en tiempo real (Real-Time Data Processing)**:

   El volumen de datos generado por sensores que reportan cada 1-5 segundos presenta desafíos de ingeniería de datos:

   - **Arquitectura de base de datos dual**: 
     - BD transaccional (PostgreSQL) optimizada para escrituras de alta frecuencia (INSERT de eventos cada segundo)
     - BD analítica (opcional: TimescaleDB, InfluxDB) para consultas de series temporales sin degradar performance transaccional

   - **Algoritmos de detección de eventos**: Diferenciar cambios de peso significativos (entrada/salida de producto) de ruido/vibración requiere algoritmos de filtrado (ventanas deslizantes, umbrales adaptativos).

   - **Balanceo latencia vs. precisión**: Alertas instantáneas (stock bajo, anomalía detectada) vs. análisis precisos que requieren mayor tiempo de procesamiento (patrones semanales, correlaciones entre productos).

   - **Escalabilidad vertical y horizontal**: El sistema debe funcionar en un laptop local (farmacia pequeña con 5 estanterías) pero también escalar a servidores cloud (distribuidora con 50 bodegas monitorizadas).

3. **Inteligencia Artificial y Machine Learning**:

   La incorporación de IA para detección de anomalías y recomendaciones predictivas enfrenta desafíos específicos:

   - **Entrenamiento con datos históricos limitados**: Startups o PYMEs nuevas no tienen años de histórico. Los modelos deben funcionar con pocos datos (few-shot learning) y mejorar progresivamente.

   - **Detección de anomalías sin saturar al usuario**: Un modelo muy sensible genera falsos positivos constantes (alarma continua) que causan "fatiga de alertas". Un modelo poco sensible deja pasar problemas reales. El balance es crítico.

   - **Adaptación continua a patrones cambiantes**: La demanda varía estacionalmente, con promociones, eventos externos (pandemia, cambios económicos). Los modelos deben reentrenarse automáticamente sin intervención de data scientists.

   - **Interpretabilidad (Explainable AI)**: Usuarios no técnicos deben entender POR QUÉ el sistema recomienda algo. "Reabastecer Producto X" es insuficiente; debe explicar "Basado en consumo de últimos 7 días y tendencia al alza detectada".

   - **Múltiples contextos simultáneos**: La IA debe analizar:
     - Patrones de inventario (rotación, quiebres)
     - Patrones de ventas (tendencias, correlaciones)
     - Patrones de movimientos (horarios pico, zonas de bodega más activas)
     - Anomalías (hurtos, errores de registro, deterioro de producto)

4. **Seguridad y Privacidad de Datos**:

   - **Cifrado end-to-end**: Datos sensibles (inventario, ventas, márgenes) deben cifrarse en tránsito (TLS/SSL) y en reposo (encriptación de BD).

   - **Control de acceso granular**: Sistema de roles (RBAC) donde bodegueros ven inventario pero no precios de costo, gerentes ven todo, auditores ven logs pero no pueden modificar.

   - **Auditoría completa (Audit Trails)**: Cada modificación debe registrar quién, cuándo, desde dónde (IP), qué cambió (antes/después). Inmutable para cumplir requisitos legales.

   - **Protección contra ataques**: Inyección SQL, XSS, CSRF, DDoS. Particularmente crítico si el sistema se expone a internet para acceso remoto.

   - **Cumplimiento GDPR/LOPD** (aunque en Chile regulación es menos estricta, prepararse para expansión internacional).

**Desafíos de Adopción y Cambio Organizacional**

1. **Resistencia al cambio (Change Management)**:

   - **Percepción de amenaza laboral**: Empleados pueden percibir la automatización como reemplazo de personas ("la máquina hará mi trabajo"). Requiere comunicación clara sobre cómo la tecnología COMPLEMENTA (libera de tareas tediosas) en lugar de reemplazar.

   - **Brecha generacional digital**: Personal de mayor edad con menor familiaridad tecnológica requiere capacitación paciente y UI/UX intuitiva (iconos claros, mensajes en lenguaje natural, no jerga técnica).

   - **Cambio de procesos arraigados**: "Siempre lo hemos hecho así" es una barrera real. La transición debe ser gradual (modo híbrido manual + automático durante período de adaptación).

2. **Curva de aprendizaje y capacitación**:

   - **Diseño de UI/UX intuitiva**: Dashboards que no requieran manual de 50 páginas. Principio de "3 clicks máximo" para cualquier tarea común.

   - **Capacitación escalonada**: 
     - Nivel 1: Usuarios operativos (consulta de stock, registro de movimientos)
     - Nivel 2: Supervisores (análisis de reportes, gestión de alertas)
     - Nivel 3: Administradores (configuración de sistema, gestión de usuarios)

   - **Soporte post-implementación**: No basta con capacitar 1 día e irse. Requiere soporte remoto/presencial durante primeras 2-4 semanas hasta que usuarios adquieran autonomía.

3. **Migración de datos legacy**:

   La transición desde sistemas anteriores (planillas Excel, cuadernos físicos, software antiguo) implica complejidad significativa:

   - **Limpieza de datos (Data Cleansing)**: 
     - Productos con nombres inconsistentes ("Paracetamol 500mg" vs. "Paracet 500" vs. "P-500")
     - Unidades de medida mezcladas (cajas, unidades, gramos)
     - Fechas en formatos diversos (DD/MM/AAAA, AAAA-MM-DD, texto libre)
     - Datos faltantes (productos sin código, sin categoría, sin proveedor)

   - **Estandarización**: Crear taxonomía unificada (categorías de productos, proveedores, ubicaciones de bodega) y mapear datos antiguos a nueva estructura.

   - **Validación de integridad**: Inventario inicial debe coincidir entre sistema antiguo y nuevo. Requiere conteo físico previo (toma de inventario completa) para establecer baseline confiable.

   - **Mantención de operaciones durante migración**: No se puede "apagar" la farmacia 1 semana para migrar. Transición debe hacerse con negocio operando (migración nocturna, modo híbrido temporal).

**Desafíos de Costo-Beneficio y Modelo de Negocio**

1. **Limitaciones presupuestarias de PYMEs**:

   - **Optimización de costos de hardware**: Balanzas industriales de precisión cuestan USD $500-$2,000 c/u. Para bodega con 20 estanterías: USD $10,000-$40,000 solo en sensores. Weigence debe:
     - Identificar sensores comerciales (COTS - Commercial Off-The-Shelf) con mejor relación costo/precisión
     - Diseñar arquitectura que funcione con sensores básicos (opcional: mejorar gradualmente)
     - Explorar fabricación local de sensores en Chile para reducir costos de importación

   - **Modelo de licenciamiento accesible**: PYMEs no pueden pagar USD $50,000 upfront. Alternativas:
     - **SaaS** (Software as a Service): Suscripción mensual $X CLP/estantería monitorizada
     - **Freemium**: Versión básica gratuita (hasta 5 estanterías), pago por funciones avanzadas (IA, multi-bodega)
     - **Pago por uso**: Cargos basados en transacciones procesadas (modelo marketplace)

   - **ROI demostrable en corto plazo**: Inversión total (hardware + software + implementación) debe recuperarse en 12-24 meses máximo, mostrando ahorros concretos (reducción de mermas, aumento de ventas por menor stock-outs).

2. **Escalabilidad económica**:

   - **Modular**: Farmacia pequeña empieza monitorizando solo 3 estanterías de productos más críticos (insulinas, controlados), expandiendo gradualmente.

   - **Multi-tenant**: Arquitectura que permite atender 100 clientes PYME desde infraestructura compartida (cloud), reduciendo costos operativos vs. instalación on-premise individual.

**Desafíos Regulatorios y de Disponibilidad**

1. **Cumplimiento normativo (Compliance)**:

   - **Trazabilidad regulatoria**: ISP exige registros de toda la cadena de custodia. Weigence debe generar reportes de auditoría en formatos requeridos (Excel, PDF firmado electrónicamente).

   - **Buenas Prácticas de Almacenamiento (BPA)**: Control de temperatura, humedad, segregación de productos incompatibles. El sistema debe integrarse (actual o futuro) con sensores ambientales.

   - **Retención de datos**: Regulaciones exigen conservar registros por 2-5 años. Arquitectura de BD debe considerar almacenamiento de largo plazo (archivado en cold storage de bajo costo).

2. **Alta disponibilidad (High Availability)**:

   - **Uptime >99.5%**: Farmacias operan 12-24 horas/día. Caídas del sistema son inaceptables (pérdida de ventas, imposibilidad de despachar).

   - **Modo offline**: Si cae internet o servidor, el sistema debe poder operar localmente (registros en dispositivo local, sincronización cuando se recupera conectividad).

   - **Backup y recuperación ante desastres**: Respaldos automáticos diarios (incremental) + semanales (completo). Plan de recuperación con RTO (Recovery Time Objective) <4 horas, RPO (Recovery Point Objective) <1 hora.

   - **Monitoreo y alertas de sistema**: Detectar proactivamente problemas (disco lleno, caída de sensor, latencia alta) antes de que afecten usuarios.

**Síntesis de Complejidad**

La resolución efectiva del problema de gestión de inventarios en PYMEs mediante tecnología IoT e IA requiere orquestar exitosamente:

- **8-12 componentes tecnológicos** (sensores, base de datos, backend API, frontend web, modelos ML, sistema de alertas, logs de auditoría, sistema de respaldos)
- **3-5 perfiles profesionales** (desarrollador backend, frontend, IoT, data scientist, diseñador UX)
- **Gestión de cambio organizacional** con capacitación y acompañamiento
- **Modelo de negocio sostenible** que sea rentable para Weigence pero accesible para PYMEs
- **Cumplimiento regulatorio** sector-específico

Esta complejidad inherente explica por qué, a pesar de la problemática evidente y los impactos económicos significativos, las PYMEs no han podido resolverlo por sí mismas ni mediante soluciones genéricas de mercado (que son enterprise, caras, y no adaptadas a realidad chilena de PYMEs).

**Weigence aborda esta complejidad** mediante:
1. Arquitectura modular que reduce complejidad técnica en componentes manejables
2. Foco en UX simple que reduce barrera de adopción
3. Implementación progresiva que distribuye costos en el tiempo
4. Validación en sector de máxima complejidad (farmacéutico) que garantiza aplicabilidad en sectores más simples

---

## 2. Levantamiento de Requerimientos

### 2.1. Determinación de los instrumentos a utilizar

### 2.2. Detalle de los requerimientos
> Se sugiere incluir como anexo el listado de los requerimientos.

---

## 3. Marco Teórico

### 3.1. Investigación Bibliográfica

---

## 4. Objetivos del Proyecto

### 4.1. Solución tecnológica

#### 4.1.1. Formulación de la Solución

#### 4.1.2. Alcance y restricciones

### 4.2. Impacto de la solución

#### 4.2.1. Proceso de negocio afectado

#### 4.2.2. Registro de Interesados

#### 4.2.3. Indicadores de gestión

#### 4.2.4. Niveles de servicio

### 4.3. Objetivos del proyecto

#### 4.3.1. Objetivo General

#### 4.3.2. Objetivo Específico

---

## 5. Metodología de Trabajo

#### 5.1.1. Metodología de Desarrollo de la solución

#### 5.1.2. Duración y cronograma

#### 5.1.3. Equipo de trabajo

#### 5.1.4. Plan de recursos

---

## 6. Definición de arquitectura TI

### 6.1. Definir el tipo de arquitectura TI que requiere la solución informática

El sistema **Weigence** implementa una **arquitectura en capas (Layered Architecture)** basada en el patrón **MVC (Model-View-Controller)** extendido, optimizada para aplicaciones web de mediana complejidad que requieren separación clara de responsabilidades, mantenibilidad y escalabilidad progresiva. Esta arquitectura es particularmente adecuada para el contexto de PYMEs debido a su balance entre simplicidad conceptual y robustez técnica.

#### 6.1.1. Justificación del Patrón Arquitectónico Seleccionado

La elección de una arquitectura en capas responde a los siguientes criterios de diseño:

**1. Separación de Responsabilidades (Separation of Concerns)**

Cada capa tiene una responsabilidad única y bien definida, permitiendo que los desarrolladores trabajen en módulos específicos sin afectar otras partes del sistema. Esto facilita:
- Desarrollo paralelo por equipos distribuidos
- Depuración localizada (errores en la capa de presentación no afectan la lógica de negocio)
- Reemplazo de componentes sin rediseño completo (ej: cambiar de Supabase a PostgreSQL local solo requiere modificar la capa de datos)

**2. Mantenibilidad y Extensibilidad**

El sistema debe evolucionar con las necesidades cambiantes de las PYMEs (nuevas funcionalidades, integración con otros sistemas, expansión a múltiples bodegas). Una arquitectura modular permite:
- Agregar nuevos módulos (ej: módulo de compras, integración con proveedores) sin refactorizar el núcleo
- Actualizar tecnologías de frontend sin tocar backend
- Implementar mejoras de seguridad en capas específicas

**3. Testabilidad**

Cada capa puede ser testeada independientemente:
- **Frontend**: Pruebas de interfaz (UI testing) y experiencia de usuario
- **Backend**: Pruebas unitarias de lógica de negocio, pruebas de integración de APIs
- **Capa de Datos**: Pruebas de consultas SQL, integridad referencial
- **Servicios de IA**: Pruebas de precisión de modelos, validación de recomendaciones

**4. Reutilización de Código**

Componentes de una capa pueden ser utilizados por múltiples módulos de capas superiores:
- El servicio de IA (`IAService`) puede ser invocado desde dashboard, inventario, ventas, y alertas
- La conexión a Supabase (`conexion_supabase.py`) es compartida por todas las rutas
- Templates base (`base.html`) son extendidos por todas las vistas específicas

#### 6.1.2. Descripción de las Capas Arquitectónicas

El sistema Weigence está estructurado en **cinco capas principales** que interactúan mediante interfaces bien definidas:

```
┌─────────────────────────────────────────────────────────────┐
│                  CAPA 1: PRESENTACIÓN                       │
│            (Frontend - Templates & Static)                  │
│  • Templates Jinja2 (HTML dinámico)                         │
│  • CSS (Bootstrap 5 + custom styles)                        │
│  • JavaScript (interactividad, AJAX, WebSockets)            │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                  CAPA 2: CONTROLADORES                      │
│                  (Backend - Routes/Flask)                   │
│  • Blueprints por módulo (login, dashboard, inventario...)  │
│  • Manejo de peticiones HTTP (GET, POST, PUT, DELETE)       │
│  • Validación de formularios y autenticación                │
│  • Enrutamiento y middleware (CSRF, rate limiting)          │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│              CAPA 3: LÓGICA DE NEGOCIO                      │
│                   (Services & Utils)                        │
│  • IAService: Servicio de recomendaciones inteligentes      │
│  • Chat Service: Lógica de mensajería tiempo real           │
│  • Utilities: Funciones auxiliares (formateo, validación)   │
│  • Business Rules: Reglas de inventario, alertas, reportes  │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│               CAPA 4: ACCESO A DATOS                        │
│                  (Data Access Layer)                        │
│  • Repositorios (IARepository, ChatModel)                   │
│  • Conexión a Supabase (conexion_supabase.py)               │
│  • Queries SQL estructuradas                                │
│  • Manejo de transacciones y errores de BD                  │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                CAPA 5: DATOS & HARDWARE                     │
│           (Database & IoT Sensors)                          │
│  • Supabase (PostgreSQL cloud)                              │
│    - Tablas: usuarios, productos, ventas, movimientos...    │
│  • Sensores IoT (balanzas inteligentes)                     │
│  • Logs de auditoría (ia_auditoria_logs)                    │
└─────────────────────────────────────────────────────────────┘
```

---

#### 6.1.3. Detalle de Interacción entre Capas

**A. CAPA 1: Presentación (Frontend)**

**Ubicación en proyecto:** `app/templates/` y `app/static/`

**Responsabilidades:**
- Renderizar interfaces de usuario dinámicas mediante plantillas Jinja2
- Gestionar interactividad del lado del cliente (validación de formularios, actualización de gráficos)
- Comunicación asíncrona con backend mediante AJAX (fetch API)
- WebSockets para funcionalidades en tiempo real (chat, notificaciones de alertas)

**Componentes principales:**

1. **Templates Jinja2** (`app/templates/`):
   - `base.html`: Plantilla maestra con estructura HTML común (navbar, sidebar, footer)
   - `pagina/dashboard.html`, `pagina/inventario.html`, `pagina/ventas.html`: Vistas específicas por módulo
   - `componentes/`: Componentes reutilizables (modals, cards, alerts)
   - `login.html`: Vista pública de autenticación

2. **Static Assets** (`app/static/`):
   - `css/`: Estilos personalizados complementando Bootstrap 5
   - `js/`: Scripts para gráficos (Chart.js), tablas interactivas (DataTables), validaciones, y AJAX
   - `uploads/`: Recursos subidos por usuarios (avatares, documentos adjuntos)

**Tecnologías:**
- **HTML5 + Jinja2**: Renderizado server-side con lógica de plantillas
- **Bootstrap 5**: Framework CSS para diseño responsive
- **JavaScript (ES6+)**: Fetch API, DOM manipulation, event handling
- **Chart.js**: Visualización de datos (gráficos de ventas, inventario)
- **Socket.IO Client**: WebSockets para chat en tiempo real

**Flujo de interacción:**

```
Usuario → [Navegador] → Renderiza template.html con datos del backend
       ↓
[Click en botón/formulario] → AJAX POST /api/inventario/agregar
       ↓
Backend procesa → Responde JSON {success: true, data: {...}}
       ↓
JavaScript actualiza DOM sin recargar página
```

---

**B. CAPA 2: Controladores (Backend - Routes)**

**Ubicación en proyecto:** `app/routes/`

**Responsabilidades:**
- Recibir peticiones HTTP desde el frontend
- Validar datos de entrada (formularios, JSON payloads)
- Invocar servicios de lógica de negocio apropiados
- Formatear respuestas (HTML renderizado o JSON para APIs)
- Gestionar sesiones de usuario y autenticación (Flask-Login)
- Aplicar middleware de seguridad (CSRF, rate limiting)

**Componentes principales:**

```python
app/routes/
├── __init__.py          # Blueprint principal 'main'
├── login.py             # Autenticación, recuperación de contraseña
├── dashboard.py         # Vista principal con resumen IA
├── inventario.py        # CRUD de productos, gestión de stock
├── ventas.py            # Registro de ventas, reportes
├── movimientos.py       # Historial de entradas/salidas
├── alertas.py           # Gestión de notificaciones
├── usuarios.py          # Administración de usuarios (solo admin)
├── perfil.py            # Edición de perfil de usuario
├── auditoria.py         # Logs de auditoría (solo admin/auditor)
├── recomendaciones_ai.py # Endpoint para recomendaciones IA
└── chat_ui.py           # Interfaz de chat 1:1
```

**Patrón de diseño:** Cada archivo implementa un **Blueprint de Flask**, que es una forma de organizar rutas relacionadas en módulos independientes.

**Ejemplo de flujo (ruta de inventario):**

```python
# app/routes/inventario.py
from flask import Blueprint, render_template, request, jsonify
from app.routes.decorators import login_required, role_required
from api.conexion_supabase import supabase

@bp.route('/inventario')
@login_required
@role_required(['administrador', 'farmacéutico', 'bodeguero'])
def inventario():
    """Renderiza vista principal de inventario"""
    productos = supabase.table('productos').select('*').execute().data
    return render_template('pagina/inventario.html', productos=productos)

@bp.route('/api/inventario/agregar', methods=['POST'])
@login_required
@role_required(['administrador', 'bodeguero'])
def agregar_producto():
    """API para agregar producto (llamada AJAX)"""
    data = request.json
    # Validación de datos...
    resultado = supabase.table('productos').insert(data).execute()
    return jsonify({'success': True, 'data': resultado.data})
```

**Middleware y seguridad:**

1. **CSRF Protection** (`flask_wtf.csrf.CSRFProtect`): Previene ataques Cross-Site Request Forgery
2. **Rate Limiting** (`flask_limiter`): Limita peticiones por IP (protección DDoS)
3. **Flask-Login**: Gestión de sesiones, decoradores `@login_required`
4. **Decoradores personalizados** (`@role_required`): Control de acceso basado en roles

---

**C. CAPA 3: Lógica de Negocio (Services)**

**Ubicación en proyecto:** `app/ia/`, `app/chat/`, `app/utils/`

**Responsabilidades:**
- Implementar reglas de negocio complejas (cálculos, validaciones, transformaciones)
- Orquestar operaciones que involucran múltiples fuentes de datos
- Proveer servicios reutilizables invocables desde múltiples controladores
- Encapsular lógica de inteligencia artificial y machine learning

**Componentes principales:**

**1. Servicio de Inteligencia Artificial** (`app/ia/`):

```python
app/ia/
├── ia_service.py              # Servicio principal (facade pattern)
├── ia_engine.py               # Motor de evaluación de reglas
├── ia_snapshots.py            # Construcción de snapshots de estado del sistema
├── ia_ml_anomalies.py         # Detección de anomalías con ML
├── ia_ml_insights_advanced.py # Análisis avanzado de patrones
├── ia_formatter.py            # Formateo de recomendaciones
├── ia_logger.py               # Logging de decisiones IA (auditoría)
├── ia_repository.py           # Acceso a datos para IA
└── ia_contexts.py             # Contextos específicos por módulo
```

**Patrón de diseño:** **Facade Pattern** - `IAService` actúa como fachada que coordina múltiples subsistemas (engine, ML, formatter, logger).

**Flujo de generación de recomendación IA:**

```python
# Invocado desde app/routes/dashboard.py
from app.ia.ia_service import IAService

ia_service = IAService()
recomendacion = ia_service.generar_recomendacion(
    contexto='dashboard',
    perfil='perfil_operativo',
    data={'usuario_id': current_user.id}
)
# Retorna: {
#   'titulo': 'Atención: Stock crítico detectado',
#   'mensaje': 'Se detectaron 3 productos bajo stock mínimo...',
#   'severidad': 'warning',
#   'solucion': 'Reabastecer productos: Paracetamol 500mg, Ibuprofeno...',
#   'confianza': 0.87
# }
```

**Proceso interno:**

1. **SnapshotBuilder** recolecta datos actuales (ventas, inventario, alertas, movimientos)
2. **IAEngine** evalúa reglas definidas según perfil de usuario
3. **ML Anomaly Detection** analiza patrones históricos para detectar anomalías
4. **IAFormatter** convierte insight técnico en mensaje comprensible
5. **AuditLogger** registra la recomendación generada en `ia_auditoria_logs`

**2. Servicio de Chat** (`app/chat/`):

```python
app/chat/
├── chat_api.py          # API REST para chat
├── chat_model.py        # Lógica de negocio (crear conversación, enviar mensaje)
├── sockets/
│   └── chat_ws.py       # WebSocket handlers (Socket.IO)
└── utils.py             # Utilidades (formateo de mensajes, notificaciones)
```

**Características:**
- Mensajería 1:1 en tiempo real mediante WebSockets
- Persistencia de mensajes en Supabase (`chat_mensajes`, `chat_conversaciones`)
- Notificaciones de mensajes no leídos
- Sistema de participantes y control de acceso

**3. Utilidades Generales** (`app/utils/`):

- `logger.py`: Sistema de logging centralizado (archivos + consola)
- `validators.py`: Validadores personalizados (RUT chileno, fechas, emails)
- `formatters.py`: Formateo de datos (moneda CLP, fechas en español, pesos)

---

**D. CAPA 4: Acceso a Datos (Data Access Layer)**

**Ubicación en proyecto:** `api/conexion_supabase.py`, `app/ia/ia_repository.py`, `app/chat/chat_model.py`

**Responsabilidades:**
- Abstraer la comunicación con la base de datos
- Proveer interfaces consistentes para operaciones CRUD
- Manejar errores de conexión y transacciones
- Implementar patrón Repository para encapsular lógica de acceso

**Componentes principales:**

**1. Conexión Base a Supabase** (`api/conexion_supabase.py`):

```python
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Cliente compartido por toda la aplicación
```

Este módulo provee una **instancia singleton** del cliente Supabase que es importada por todos los componentes que necesitan acceso a datos.

**2. Repositorios Especializados**:

**IARepository** (`app/ia/ia_repository.py`):
```python
class IARepository:
    """Wrapper around Supabase queries used by the IA engine."""
    
    def obtener_ventas_desde(self, desde: datetime) -> List[Dict]:
        """Obtiene ventas desde fecha específica para análisis de tendencias"""
        return supabase.table('ventas')\
            .select('*')\
            .gte('fecha_venta', desde.isoformat())\
            .execute().data
    
    def obtener_alertas_activas(self) -> List[Dict]:
        """Obtiene alertas no resueltas"""
        return supabase.table('alertas')\
            .select('*')\
            .eq('estado', 'activa')\
            .execute().data
    
    def registrar_auditoria_ia(self, payload: Dict) -> bool:
        """Persiste logs de decisiones IA"""
        try:
            supabase.table('ia_auditoria_logs').insert(payload).execute()
            return True
        except Exception as e:
            logger.error(f"Error registrando auditoría IA: {e}")
            return False
```

**ChatModel** (`app/chat/chat_model.py`):
```python
def obtener_conversaciones_usuario(usuario_id: str):
    """Obtiene conversaciones donde el usuario es participante"""
    return supabase.table('chat_participantes')\
        .select('conversacion_id, chat_conversaciones(*)')\
        .eq('usuario_id', usuario_id)\
        .execute().data

def enviar_mensaje(conversacion_id: str, usuario_id: str, contenido: str):
    """Inserta mensaje en BD y retorna el registro creado"""
    mensaje = {
        'conversacion_id': conversacion_id,
        'usuario_id': usuario_id,
        'contenido': contenido,
        'fecha_envio': datetime.now().isoformat()
    }
    return supabase.table('chat_mensajes').insert(mensaje).execute().data[0]
```

**Patrón de diseño:** **Repository Pattern** - Encapsula lógica de acceso a datos, permitiendo:
- Cambiar de Supabase a PostgreSQL local sin modificar lógica de negocio
- Testear servicios con repositorios mock (sin necesidad de BD real)
- Centralizar manejo de errores de BD

---

**E. CAPA 5: Datos & Hardware (Database & IoT)**

**Componentes:**

**1. Supabase (PostgreSQL Cloud)**

Supabase es una plataforma Backend-as-a-Service (BaaS) que provee:
- **PostgreSQL** gestionado con backups automáticos
- **API REST** autogenerada desde schema de BD
- **Autenticación** (aunque Weigence usa autenticación custom con Flask-Login)
- **Storage** para archivos (futura implementación para avatares, documentos)
- **Realtime subscriptions** (WebSockets nativos de PostgreSQL, no utilizados actualmente)

**Estructura de Base de Datos (principales tablas):**

```sql
-- Usuarios y autenticación
usuarios (
    rut_usuario VARCHAR PRIMARY KEY,
    nombre VARCHAR,
    correo VARCHAR,
    rol VARCHAR, -- 'administrador', 'farmacéutico', 'bodeguero', 'auditor'
    Contraseña TEXT, -- bcrypt hash
    numero_celular VARCHAR,
    fecha_registro TIMESTAMP,
    reset_token VARCHAR,
    reset_token_expires TIMESTAMP
)

-- Productos e inventario
productos (
    idproducto SERIAL PRIMARY KEY,
    nombre VARCHAR,
    categoria VARCHAR,
    stock INTEGER,
    precio_unitario DECIMAL,
    peso DECIMAL,
    id_estante INTEGER,
    fecha_ingreso TIMESTAMP,
    ingresado_por VARCHAR REFERENCES usuarios(rut_usuario)
)

-- Estanterías con sensores IoT
estantes (
    id_estante SERIAL PRIMARY KEY,
    nombre VARCHAR,
    categoria VARCHAR,
    peso_maximo DECIMAL,
    peso_actual DECIMAL,
    coord_x INTEGER,
    coord_y INTEGER,
    estado VARCHAR,
    ultima_actualizacion TIMESTAMP
)

-- Ventas
ventas (
    idventa SERIAL PRIMARY KEY,
    rut_usuario VARCHAR REFERENCES usuarios(rut_usuario),
    fecha_venta TIMESTAMP,
    total DECIMAL
)

detalle_ventas (
    iddetalle SERIAL PRIMARY KEY,
    idventa INTEGER REFERENCES ventas(idventa),
    idproducto INTEGER REFERENCES productos(idproducto),
    cantidad INTEGER,
    precio_unitario DECIMAL,
    subtotal DECIMAL,
    fecha_detalle TIMESTAMP
)

-- Movimientos de inventario
movimientos_inventario (
    id_movimiento SERIAL PRIMARY KEY,
    idproducto INTEGER REFERENCES productos(idproducto),
    id_estante INTEGER REFERENCES estantes(id_estante),
    rut_usuario VARCHAR REFERENCES usuarios(rut_usuario),
    tipo_evento VARCHAR, -- 'entrada', 'salida', 'ajuste', 'vencimiento'
    cantidad INTEGER,
    timestamp TIMESTAMP,
    observacion TEXT
)

-- Alertas
alertas (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR,
    descripcion TEXT,
    tipo_color VARCHAR, -- 'warning', 'danger', 'info'
    icono VARCHAR,
    estado VARCHAR, -- 'activa', 'resuelta'
    idproducto INTEGER REFERENCES productos(idproducto),
    idusuario VARCHAR REFERENCES usuarios(rut_usuario),
    fecha_creacion TIMESTAMP
)

-- Auditoría
auditoria_eventos (
    id SERIAL PRIMARY KEY,
    fecha TIMESTAMP,
    usuario VARCHAR,
    accion VARCHAR, -- 'login', 'modificacion_producto', 'venta', etc.
    detalle JSONB
)

-- Logs de IA
ia_auditoria_logs (
    id SERIAL PRIMARY KEY,
    fecha_generacion TIMESTAMP,
    tipo VARCHAR, -- 'dashboard', 'inventario', 'ventas', etc.
    severidad VARCHAR, -- 'info', 'warning', 'critical'
    titulo VARCHAR,
    mensaje TEXT,
    solucion TEXT,
    metadata JSONB,
    confianza DECIMAL
)

-- Chat
chat_conversaciones (
    id UUID PRIMARY KEY,
    nombre VARCHAR,
    es_grupal BOOLEAN,
    creado_por VARCHAR REFERENCES usuarios(rut_usuario),
    fecha_creacion TIMESTAMP,
    ultima_actualizacion TIMESTAMP
)

chat_participantes (
    id UUID PRIMARY KEY,
    conversacion_id UUID REFERENCES chat_conversaciones(id),
    usuario_id VARCHAR REFERENCES usuarios(rut_usuario),
    ultimo_mensaje_leido UUID,
    fecha_ingreso TIMESTAMP
)

chat_mensajes (
    id UUID PRIMARY KEY,
    conversacion_id UUID REFERENCES chat_conversaciones(id),
    usuario_id VARCHAR REFERENCES usuarios(rut_usuario),
    contenido TEXT,
    fecha_envio TIMESTAMP,
    editado BOOLEAN,
    eliminado BOOLEAN
)
```

**2. Sensores IoT (Hardware Futuro/Prototipo)**

Si bien actualmente el sistema funciona con entrada manual de datos, la arquitectura está preparada para integrar:

- **Balanzas inteligentes** conectadas a estanterías que reportan peso en tiempo real
- **Protocolo de comunicación:** MQTT o HTTP POST a endpoint `/api/sensor/peso`
- **Procesamiento:** Los datos de peso se comparan con peso unitario de productos para calcular stock automáticamente
- **Tabla de pesajes:**

```sql
pesajes (
    id SERIAL PRIMARY KEY,
    id_estante INTEGER REFERENCES estantes(id_estante),
    idproducto INTEGER REFERENCES productos(idproducto),
    peso_medido DECIMAL,
    timestamp TIMESTAMP,
    pesado_por VARCHAR REFERENCES usuarios(rut_usuario)
)
```

---

#### 6.1.4. Flujo Completo de una Operación (Ejemplo: Visualizar Dashboard con Recomendaciones IA)

Para ilustrar la interacción entre capas, se describe el flujo completo desde que un usuario accede al dashboard hasta que visualiza recomendaciones personalizadas:

```
┌─────────────────────────────────────────────────────────────┐
│  PASO 1: Usuario abre http://localhost:5000/dashboard       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  CAPA 2: app/routes/dashboard.py                            │
│  @bp.route('/dashboard')                                    │
│  @login_required                                            │
│  def dashboard():                                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  CAPA 3: Invoca IAService                                   │
│  ia_service = IAService()                                   │
│  recomendacion = ia_service.generar_recomendacion(          │
│      contexto='dashboard',                                  │
│      perfil='perfil_operativo'                              │
│  )                                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  CAPA 3: IAService internamente ejecuta:                    │
│  1. SnapshotBuilder.build() → construye estado actual       │
│  2. IAEngine.evaluate() → aplica reglas de negocio          │
│  3. detect_anomalies() → ejecuta modelo ML                  │
│  4. IAFormatter.render() → formatea mensaje                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  CAPA 4: IARepository consulta Supabase                     │
│  - ventas_recientes = obtener_ventas_desde(hace_7_dias)     │
│  - alertas = obtener_alertas_activas()                      │
│  - movimientos = obtener_movimientos_recientes()            │
│  - productos = obtener_productos_bajo_stock()               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  CAPA 5: Supabase (PostgreSQL)                              │
│  - Ejecuta queries SQL                                      │
│  - Retorna datos JSON                                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  CAPA 4: IARepository retorna datos estructurados           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  CAPA 3: IAService procesa datos                            │
│  - ML detecta anomalía: "Caída 15% en ventas vs semana ant" │
│  - Engine determina severidad: "warning"                    │
│  - Formatter genera mensaje legible                         │
│  - AuditLogger registra en ia_auditoria_logs                │
│  Retorna: {titulo, mensaje, severidad, solucion, confianza} │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  CAPA 2: dashboard.py recibe recomendacion                  │
│  return render_template('pagina/dashboard.html',            │
│      recomendacion=recomendacion,                           │
│      usuario=current_user                                   │
│  )                                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  CAPA 1: Jinja2 renderiza dashboard.html                    │
│  - Muestra tarjeta de alerta con recomendacion.titulo       │
│  - Color según recomendacion.severidad (warning=amarillo)   │
│  - Gráfico Chart.js con datos de ventas                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Usuario visualiza dashboard con recomendación IA           │
│  "⚠️ Atención: Ventas cayeron 15% respecto a semana previa" │
│  "Solución: Revisar productos de baja rotación..."          │
└─────────────────────────────────────────────────────────────┘
```

---

#### 6.1.5. Ventajas de la Arquitectura en Capas para Weigence

**1. Mantenibilidad**

- **Localización de cambios:** Un cambio en la lógica de cálculo de stock solo afecta `app/ia/ia_snapshots.py`, sin tocar frontend ni BD.
- **Depuración eficiente:** Errores en la interfaz se resuelven en templates/static; errores de datos en repositorios; errores de lógica en servicios.
- **Documentación modular:** Cada capa tiene responsabilidades claras documentables independientemente.

**2. Escalabilidad**

- **Escalabilidad horizontal (frontend):** Agregar servidores nginx para servir static files sin tocar backend.
- **Escalabilidad de servicios:** Mover `IAService` a microservicio independiente si el procesamiento ML requiere más recursos.
- **Escalabilidad de BD:** Migrar de Supabase a PostgreSQL auto-gestionado o cluster solo requiere cambiar `conexion_supabase.py`.

**3. Reutilización**

- **IAService** es invocado desde dashboard, inventario, ventas, alertas → Una sola implementación, múltiples consumidores.
- **Templates base** (`base.html`) son extendidos por todas las vistas → Cambiar navbar una vez, afecta todas las páginas.
- **Decoradores** (`@login_required`, `@role_required`) se aplican a múltiples rutas → Seguridad centralizada.

**4. Testabilidad**

- **Pruebas unitarias de servicios:** Testear `IAService` con repositorios mock sin necesidad de BD real.
- **Pruebas de integración:** Testear flujo completo controlador → servicio → BD con BD de prueba.
- **Pruebas de interfaz:** Selenium/Playwright para testear frontend sin preocuparse por implementación de backend.

**5. Adaptabilidad tecnológica**

- **Cambio de BD:** De Supabase a PostgreSQL local, MongoDB, o MySQL → Solo modificar capa 4.
- **Cambio de framework frontend:** De templates Jinja2 a SPA (React/Vue) → Solo modificar capa 1, backend expone APIs JSON.
- **Migración a microservicios:** Separar IA, Chat, Inventario en servicios independientes → Preservar interfaces de capa 2.

---

#### 6.1.6. Consideraciones de Seguridad por Capa

**Capa 1 (Frontend):**
- Validación client-side (JavaScript) como primera barrera, pero NO confiable (puede ser bypasseada)
- Content Security Policy (CSP) para prevenir XSS
- HTTPS obligatorio en producción

**Capa 2 (Controladores):**
- **CSRF tokens** en todos los formularios
- **Validación server-side** de todos los inputs (nunca confiar en frontend)
- **Rate limiting** para prevenir brute force (login, APIs)
- **Sanitización de inputs** antes de pasar a capa de datos

**Capa 3 (Servicios):**
- **Validación de reglas de negocio** (ej: solo admin puede eliminar usuarios)
- **Logging de decisiones críticas** (auditoría de acciones sensibles)

**Capa 4 (Datos):**
- **Queries parametrizadas** (Supabase/ORM previene SQL injection)
- **Control de acceso a BD** (usuario de BD con permisos mínimos necesarios)

**Capa 5 (BD):**
- **Cifrado en reposo** (datos sensibles como contraseñas con bcrypt)
- **Backups automáticos** diarios con retención de 7-30 días
- **Row-Level Security (RLS)** en Supabase para multi-tenancy futuro

---

### Conclusión

La arquitectura en capas implementada en Weigence provee un equilibrio óptimo entre:
- **Simplicidad conceptual:** Fácil de comprender para equipos de desarrollo pequeños (2-5 personas)
- **Robustez técnica:** Separación de responsabilidades que facilita mantenimiento y testing
- **Escalabilidad progresiva:** Permite evolucionar desde PYME pequeña (1 bodega) a mediana (múltiples sucursales) sin rediseño arquitectónico
- **Adaptabilidad:** Facilita migración tecnológica (cambio de BD, framework, o infraestructura) con impacto localizado

Esta arquitectura es especialmente adecuada para el contexto de PYMEs chilenas, donde el desarrollo es iterativo, los equipos técnicos son reducidos, y la solución debe ser mantenible sin depender de especialistas enterprise de alto costo.

---

## 7. Reconocimiento de arquitectura empresarial

### 7.1. Identificación del tipo de organización y su estructura

---

## 8. Detalle de las Tecnologías a implementar

### 8.1. Análisis cualitativo/cuantitativo de las tecnologías que serán implementadas

### 8.2. Herramientas, aplicaciones, lenguajes y componentes que serán implementados

La implementación de Weigence requiere un stack tecnológico heterogéneo que integra hardware IoT, backend, base de datos, frontend y servicios auxiliares. A continuación se presenta el detalle completo de cada tecnología, su rol específico, justificación técnica y características relevantes:

#### Tabla 8.2.1: Componentes de Hardware IoT

| **Componente** | **Modelo/Especificación** | **Función** | **Justificación** | **Características Técnicas** |
|----------------|---------------------------|-------------|-------------------|------------------------------|
| **Celda de carga** | Single-point load cell 1-10kg | Transductor fuerza → señal eléctrica | Medición directa de peso para detectar variaciones de inventario | • Capacidad nominal: 1-10kg según estante<br>• Sensibilidad: mV/V<br>• Precisión: ±0.02% full scale<br>• Material: Aleación de aluminio<br>• Conexión: 4 cables (E+, E-, S+, S-) |
| **HX711** | Conversor ADC 24 bits | Digitalización señal analógica de celda | Resolución de 24 bits permite detectar cambios pequeños (gramos) | • Resolución: 24 bits<br>• Ganancia seleccionable: 32/64/128<br>• Tasa de muestreo: 10/80 SPS<br>• Voltaje operación: 2.6-5.5V<br>• Interfaz: 2-wire (PD_SCK, DOUT)<br>• Ruido: <±50μV @ 10 SPS |
| **Raspberry Pi Pico W** | RP2040 + WiFi Infineon CYW43439 | Microcontrolador con conectividad WiFi | WiFi integrado elimina módulos externos, bajo costo, MicroPython nativo | • Procesador: Dual-core ARM Cortex-M0+ @ 133 MHz<br>• Memoria: 264KB SRAM, 2MB Flash<br>• WiFi: 2.4GHz 802.11n<br>• GPIO: 26 pines multifunción<br>• Consumo: ~120mA @ 133MHz WiFi activo<br>• Precio: ~$6 USD |
| **Fuente USB 5V** | Micro USB 5V/1A mínimo | Alimentación eléctrica nodo IoT | Estabilidad crítica para lecturas precisas del ADC | • Voltaje: 5V ±5%<br>• Corriente: ≥1A<br>• Regulación recomendada para evitar deriva térmica |

---

#### Tabla 8.2.2: Stack de Desarrollo de Firmware IoT

| **Tecnología** | **Versión** | **Función** | **Justificación** | **Lenguaje/Sintaxis** |
|----------------|-------------|-------------|-------------------|-----------------------|
| **MicroPython** | 1.20+ | Lenguaje interpretado para microcontroladores | Curva de aprendizaje reducida vs C/C++, ecosistema maduro, debugging rápido | Python 3.x subset optimizado para recursos limitados |
| **Librería `machine`** | Built-in MicroPython | Control hardware GPIO, I2C, SPI | Interfaz estandarizada para comunicación con HX711 y WiFi | API orientada a objetos (`machine.Pin`, `machine.SPI`) |
| **Librería `network`** | Built-in MicroPython | Gestión conexión WiFi | Conexión automática a AP, manejo de reconexión ante caídas | `network.WLAN(network.STA_IF)` |
| **Librería `urequests`** | MicroPython port de requests | Cliente HTTP para envío de datos | POST hacia backend Flask, serialización JSON | Similar a `requests` de CPython |
| **Thonny IDE** | 4.x | Entorno desarrollo e instalación firmware | IDE oficial Raspberry Pi, upload directo a Pico, REPL integrado | Python IDE con soporte MicroPython nativo |

---

#### Tabla 8.2.3: Backend - Framework y Librerías Python

| **Componente** | **Versión** | **Función** | **Justificación** | **Características** |
|----------------|-------------|-------------|-------------------|---------------------|
| **Flask** | 3.0.3 | Microframework web Python | Simplicidad, modularidad (Blueprints), bajo overhead vs Django | • Routing declarativo<br>• WSGI-compliant<br>• Extensible vía plugins<br>• Sin ORM obligatorio |
| **Python** | 3.10-3.12 | Lenguaje base backend | Integración con ecosistema científico (NumPy, Pandas), librerías ML, productividad | Lenguaje interpretado multiparadigma |
| **Flask-Login** | 0.6.3 | Gestión sesiones usuario | Sistema de autenticación ligero, decoradores `@login_required` | • Session management<br>• User loader callback<br>• Remember me cookies |
| **Flask-WTF** | 1.2.1 | Forms y CSRF protection | Protección automática CSRF en formularios, validación server-side | Integración WTForms + CSRF tokens |
| **Werkzeug** | 3.0.1 | Utilidades WSGI y seguridad | Hashing bcrypt para contraseñas, manejo de rutas, depuración | • Password hashing (bcrypt/scrypt)<br>• Secure filename<br>• Debug toolbar |
| **python-dotenv** | 1.0.1 | Gestión variables entorno | Cargar credenciales (Supabase URL/Key) desde `.env` sin hardcodear | Lee pares `KEY=VALUE` desde archivo `.env` |
| **supabase-py** | 2.5.0 | Cliente Python Supabase | SDK oficial para PostgreSQL vía REST API, RLS integrado | • Query builder<br>• Auth helpers<br>• Realtime subscriptions (opcional) |
| **Flask-SocketIO** | 5.3.6 | WebSockets para chat tiempo real | Bidireccional, soporte rooms, fallback a polling | Basado en python-socketio + engineio |
| **Jinja2** | 3.1.3 | Motor de templates server-side | Renderizado HTML dinámico con sintaxis Python-like, herencia de templates | • Template inheritance<br>• Filters y macros<br>• Auto-escaping XSS |

---

#### Tabla 8.2.4: Base de Datos y Servicios en la Nube

| **Servicio** | **Tipo** | **Función** | **Justificación** | **Especificaciones** |
|--------------|----------|-------------|-------------------|----------------------|
| **Supabase** | BaaS (Backend as a Service) | Plataforma base de datos gestionada | PostgreSQL gestionado, API REST autogenerada, RLS, backups automáticos | • Hosting: Cloud multi-región<br>• Plan gratuito: 500MB DB + 1GB bandwidth/mes<br>• Escalabilidad: Hasta dedicated instances |
| **PostgreSQL** | 15.x | Motor base de datos relacional | ACID, integridad referencial, consultas complejas, auditoría | • Modelo relacional<br>• Transacciones ACID<br>• Triggers y stored procedures<br>• JSON/JSONB nativo |
| **Row Level Security (RLS)** | Feature PostgreSQL | Control acceso granular por fila | Políticas de seguridad a nivel de base de datos sin lógica en backend | Ejemplo: `usuarios` solo ven sus propios registros |
| **PostgREST** | API REST autogenerada | Capa API sobre PostgreSQL | Supabase expone tablas como endpoints REST automáticamente | • GET/POST/PATCH/DELETE<br>• Filtros via query params<br>• Auth via JWT |

---

#### Tabla 8.2.5: Tablas de Base de Datos Principales

| **Tabla** | **Función** | **Campos Clave** | **Relaciones** |
|-----------|-------------|------------------|----------------|
| `usuarios` | Gestión usuarios y autenticación | `rut_usuario` (PK), `nombre`, `correo`, `rol`, `Contraseña` (bcrypt), `numero_celular` | → `ventas`, `movimientos_inventario`, `chat_conversaciones` |
| `productos` | Catálogo productos | `idproducto` (PK), `nombre`, `categoria`, `stock`, `precio_unitario`, `peso`, `id_estante` (FK) | → `detalle_ventas`, `movimientos_inventario`, `alertas` |
| `estantes` | Ubicación física con sensores | `id_estante` (PK), `nombre`, `categoria`, `peso_maximo`, `peso_actual`, `coord_x`, `coord_y`, `estado` | → `productos`, `movimientos_inventario` |
| `ventas` | Registro transacciones venta | `idventa` (PK), `rut_usuario` (FK), `fecha_venta`, `total` | → `detalle_ventas` |
| `detalle_ventas` | Líneas de venta (productos) | `iddetalle` (PK), `idventa` (FK), `idproducto` (FK), `cantidad`, `subtotal` | ← `ventas`, `productos` |
| `movimientos_inventario` | Auditoría movimientos stock | `id_movimiento` (PK), `idproducto` (FK), `id_estante` (FK), `rut_usuario` (FK), `tipo_evento`, `cantidad`, `timestamp` | ← `productos`, `estantes`, `usuarios` |
| `alertas` | Notificaciones operativas | `id` (PK), `titulo`, `descripcion`, `tipo_color` (warning/danger/info), `estado` (activa/resuelta), `idproducto` (FK) | ← `productos` |
| `auditoria_eventos` | Logs sistema completo | `id` (PK), `fecha`, `usuario`, `accion` (login/modificacion/venta), `detalle` (JSONB) | Registro de todas las acciones críticas |
| `ia_auditoria_logs` | Logs recomendaciones IA | `id` (PK), `fecha_generacion`, `tipo` (dashboard/inventario/ventas), `severidad` (info/warning/critical), `mensaje`, `metadata` (JSONB) | Historial decisiones motor IA |
| `chat_conversaciones` | Conversaciones chat 1:1 | `id` (UUID PK), `nombre`, `es_grupal`, `creado_por` (FK), `fecha_creacion` | → `chat_participantes`, `chat_mensajes` |
| `chat_mensajes` | Mensajes individuales | `id` (UUID PK), `conversacion_id` (FK), `usuario_id` (FK), `contenido`, `fecha_envio` | ← `chat_conversaciones` |
| `pesajes` | Lecturas sensores IoT | `id` (PK), `id_estante` (FK), `idproducto` (FK), `peso_medido`, `timestamp`, `pesado_por` (FK) | ← `estantes`, `productos`, `usuarios` |

---

#### Tabla 8.2.6: Frontend - Tecnologías de Interfaz

| **Tecnología** | **Versión** | **Función** | **Justificación** | **Características** |
|----------------|-------------|-------------|-------------------|---------------------|
| **HTML5** | Estándar W3C | Estructura markup páginas | Semántico, accesible, compatible con todos los navegadores modernos | • Tags semánticos (`<nav>`, `<article>`)<br>• Formularios validables<br>• APIs modernas (localStorage, fetch) |
| **Tailwind CSS** | 3.4.x | Framework CSS utility-first | Desarrollo rápido sin escribir CSS custom, responsive por defecto, tamaño optimizado con PurgeCSS | • Clases utilitarias (`flex`, `p-4`, `bg-blue-500`)<br>• Responsive prefixes (`md:`, `lg:`)<br>• Dark mode built-in<br>• JIT compiler |
| **JavaScript (Vanilla ES6+)** | ECMAScript 2015+ | Interactividad cliente | Fetch API para AJAX, manipulación DOM, validaciones client-side | • Arrow functions<br>• Promises y async/await<br>• Modules (import/export)<br>• Template literals |
| **Chart.js** | 4.x | Gráficos y visualizaciones | Librería ligera para dashboards, gráficos responsivos, animaciones suaves | • Line, bar, pie, doughnut charts<br>• Responsive & animado<br>• Plugins extensibles |
| **DataTables** | 1.13.x | Tablas interactivas | Búsqueda, ordenamiento, paginación client-side, exportación a Excel/PDF | • jQuery plugin<br>• Integración con Bootstrap<br>• Server-side processing opcional |
| **Socket.IO Client** | 4.6.x | WebSockets bidireccional | Chat en tiempo real, notificaciones live, sincronización eventos | • Auto-reconnect<br>• Fallback a polling<br>• Rooms y namespaces |
| **Jinja2 Templates** | 3.1.3 (server) | Renderizado server-side | Variables dinámicas, herencia templates, lógica condicional en HTML | • Template inheritance (`{% extends %}`)<br>• Loops y condicionales<br>• Filters (`|date`, `|upper`) |

---

#### Tabla 8.2.7: Seguridad y Control de Acceso

| **Mecanismo** | **Implementación** | **Función** | **Tecnología Base** |
|---------------|-------------------|-------------|---------------------|
| **RBAC (Role-Based Access Control)** | Decorador `@role_required(['administrador'])` | Control acceso por roles (administrador, supervisor, operador) | Flask decorators + sesiones |
| **CSRF Protection** | Tokens CSRF en formularios | Prevención Cross-Site Request Forgery | Flask-WTF (`CSRFProtect`) |
| **Bcrypt Password Hashing** | `werkzeug.security.generate_password_hash()` | Hashing unidireccional contraseñas | Werkzeug + bcrypt algorithm |
| **Session Management** | Flask-Login + cookies seguras | Persistencia sesión usuario autenticado | Flask sessions + `httponly` cookies |
| **SQL Injection Prevention** | Queries parametrizadas Supabase client | Evitar inyección SQL | PostgREST parameterized queries |
| **XSS Protection** | Auto-escaping Jinja2 | Escapar HTML en templates | Jinja2 autoescape activado por defecto |

---

#### Tabla 8.2.8: Inteligencia Artificial y Análisis

| **Componente** | **Tecnología** | **Función** | **Algoritmo/Método** |
|----------------|----------------|-------------|----------------------|
| **Motor IA Contextual** | Python custom (`ia_service.py`) | Generación recomendaciones operativas basadas en reglas y patrones | • Rule-based engine<br>• Pattern matching<br>• Threshold detection |
| **Detección Anomalías** | `ia_ml_anomalies.py` | Identificar comportamiento inusual (ventas, movimientos, quiebres) | • Isolation Forest (scikit-learn)<br>• Análisis estadístico básico<br>• Umbrales dinámicos |
| **Snapshot Builder** | `ia_snapshots.py` | Construir estado actual sistema (inventario, alertas, ventas) | Agregación datos de múltiples tablas |
| **IA Formatter** | `ia_formatter.py` | Traducir insights técnicos → mensajes legibles | Templates mensajes + lógica severidad (info/warning/critical) |
| **Audit Logger IA** | `ia_logger.py` | Registrar decisiones IA en tabla `ia_auditoria_logs` | INSERT log con metadata JSONB |

---

#### Tabla 8.2.9: Herramientas de Desarrollo y Colaboración

| **Herramienta** | **Versión** | **Función** | **Uso en Proyecto** |
|----------------|-------------|-------------|---------------------|
| **Visual Studio Code** | 1.85+ | IDE principal desarrollo | Edición código, debugging Python, extensiones (Pylance, Python, GitLens) |
| **Git** | 2.40+ | Control versiones | Commits, branches, merge, historial código |
| **GitHub** | Cloud | Repositorio remoto y colaboración | • Repositorio central<br>• Pull requests<br>• Issues tracking<br>• Actions (CI/CD opcional) |
| **Postman** | 10.x | Testing APIs REST | Pruebas endpoints Flask y Supabase API |
| **Chrome DevTools** | Built-in Chrome | Debug frontend y network | • Inspeccionar elementos<br>• Console JS<br>• Network tab (XHR)<br>• WebSocket monitoring |
| **Thonny** | 4.1.x | IDE MicroPython | Upload firmware a Pico W, REPL directo, debugging sensor |

---

#### Tabla 8.2.10: Protocolos y Estándares de Comunicación

| **Protocolo** | **Capa OSI** | **Uso en Weigence** | **Especificación** |
|---------------|--------------|---------------------|-------------------|
| **HTTP/HTTPS** | Aplicación (7) | • Frontend ↔ Backend<br>• Pico W → Backend<br>• Backend → Supabase API | • HTTP/1.1<br>• HTTPS con TLS 1.2/1.3<br>• Métodos: GET, POST, PUT, DELETE |
| **WebSocket (WSS)** | Aplicación (7) | Chat en tiempo real bidireccional | • Socket.IO protocol<br>• Fallback: Long polling |
| **WiFi 802.11n** | Física (1) / Enlace (2) | Conectividad Pico W → Router local | • 2.4 GHz<br>• WPA2-PSK seguridad mínima |
| **JSON** | Serialización | Formato intercambio datos universal | • RFC 8259<br>• Content-Type: application/json |
| **RESTful API** | Arquitectura | Diseño endpoints backend Flask y Supabase | • Stateless<br>• CRUD via HTTP verbs<br>• Resource-based URLs |

---

#### Tabla 8.2.11: Módulos Funcionales de la Plataforma Web

| **Módulo** | **Ruta Flask** | **Función** | **Roles con Acceso** | **Tecnologías Clave** |
|------------|----------------|-------------|----------------------|-----------------------|
| **Login/Auth** | `/login`, `/logout` | Autenticación usuarios | Todos (público login) | Flask-Login, bcrypt, sesiones |
| **Dashboard** | `/dashboard` | Vista principal con KPIs e IA header | Todos autenticados | Chart.js, IA contextual, Jinja2 |
| **Inventario** | `/inventario` | CRUD productos, visualización stock | Administrador, Supervisor | DataTables, modals Bootstrap |
| **Movimientos** | `/movimientos` | Historial entradas/salidas (automático + manual) | Todos autenticados | Filtros fecha, DataTables |
| **Ventas** | `/ventas`, `/ventas/registrar` | Registro ventas, detalle productos vendidos | Administrador, Supervisor | Forms Flask-WTF, cálculos JS |
| **Alertas** | `/alertas` | Gestión notificaciones (stock bajo, anomalías) | Administrador, Supervisor | Badges Tailwind, filtros estado |
| **Auditoría** | `/auditoria` | Logs completos sistema + recomendaciones IA extensas | Administrador, Auditor | JSONB queries, análisis IA |
| **Usuarios** | `/usuarios` | Gestión usuarios, roles, permisos | Solo Administrador | CRUD con validación RUT, RBAC |
| **Perfil** | `/perfil` | Edición perfil usuario actual | Todos autenticados | Forms, validación contraseña |
| **Chat** | `/chat` | Mensajería 1:1 tiempo real | Todos autenticados | Socket.IO, WebSockets |

---

#### Tabla 8.2.12: Variables de Entorno y Configuración

| **Variable** | **Función** | **Ejemplo Valor** | **Seguridad** |
|--------------|-------------|-------------------|---------------|
| `SUPABASE_URL` | URL instancia Supabase | `https://xxxxx.supabase.co` | Pública (no sensible) |
| `SUPABASE_KEY` | API Key Supabase (anon o service_role) | `eyJhbGciOiJIUz...` | **Secreta** (no commitear) |
| `FLASK_SECRET_KEY` | Clave secreta Flask para sesiones | `random_string_256_bits` | **Secreta** |
| `FLASK_ENV` | Entorno ejecución | `development` / `production` | Pública |
| `WIFI_SSID` | SSID red WiFi (Pico W) | `Mi_Router_WiFi` | Configuración local |
| `WIFI_PASSWORD` | Contraseña WiFi | `contraseña_segura` | **Secreta** |

---

### Resumen de Justificación del Stack Tecnológico

El stack seleccionado para Weigence responde a tres criterios fundamentales:

1. **Accesibilidad económica**: Hardware IoT de bajo costo (~$15 USD/nodo completo), servicios cloud con plan gratuito viable (Supabase), frameworks open-source sin licencias.

2. **Curva de aprendizaje manejable**: Python en backend y firmware (MicroPython), evitando lenguajes de bajo nivel (C/C++) innecesarios para MVP. HTML/CSS/JS estándar sin frameworks SPA complejos.

3. **Escalabilidad progresiva**: Arquitectura modular permite:
   - Agregar estantes = agregar nodos Pico W independientes
   - Mejorar IA = modificar `ia_service.py` sin tocar IoT ni frontend
   - Migrar BD = cambiar capa de acceso (`conexion_supabase.py`) sin refactorizar lógica

Esta arquitectura tecnológica permite a una PYME operar un sistema de inventario automatizado con inversión inicial < $100 USD (excluyendo servidor, que puede ser hosting compartido económico o incluso localhost durante pruebas) y mantenimiento técnico bajo, sin dependencia de especialistas externos para tareas rutinarias.

---

## 9. Detalle de la Arquitectura a implementar

### 9.1. Diagrama BPMN

### 9.2. Diagramas de caso de uso

### 9.3. Diagrama de componentes

### 9.4. Modelo de dato

### 9.5. Topología de comunicaciones

### 9.6. Diagrama de Infraestructura

### 9.7. Diagrama de Arquitectura

---

## 10. Implementación de los KPI y SLA

### 10.1. Descripción de KPI

### 10.2. Descripción de SLA

---

## Plan de Pruebas y Aseguramiento de Calidad

### 10.3. Plan de Pruebas

### 10.4. Normas y Estándares

---

## 11. Plan de Implementación

### 11.1. Gestión de Disponibilidad

### 11.2. Gestión de Continuidad

### 11.3. Plan de Mantención

---

## 12. Defensa de Proyecto

### 12.1. Argumentación técnica

### 12.2. Factibilidad técnica

### 12.3. Factibilidad económica

### 12.4. Factibilidad legal y ambiental

### 12.5. Presentación de la solución

### 12.6. Funcionalidad

### 12.7. Sustentabilidad

### 12.8. Retroalimentación

### 12.9. Valor al negocio

### 12.10. Propuestas futuras

---

**Documento generado**: Diciembre 3, 2025  
**Proyecto**: Sistema de Gestión de Inventario Weigence  
**Estado**: Borrador inicial
