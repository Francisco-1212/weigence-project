
TÍTULO DEL TRABAJO DE SEMINARIO:
Sistema inteligente de gestión de inventarios mediante pesaje automático “Weigence”
autores:
Paulo Brito 
Francisco Carrasco
Nelson Duarte

TRABAJO DE SEMINARIO, presentado en cumplimiento parcial de los requisitos para optar al título de Ingeniero en Informática de la Universidad Tecnológica de Chile INACAP, sede Renca

Comisión Examinadora:


Sr(a) 



Sr(a) 



Sr(a) 



Sr(a) 



Sr(a) 





nota obtenida: 
Declaración de autoría
Nosotros, Paulo Brito, Francisco Carrasco y Nelsonl Duarte, declaramos bajo nuestra responsabilidad que el presente trabajo de tesis es de nuestra autoría y corresponde a un desarrollo original elaborado exclusivamente por este equipo. Afirmamos que el contenido aquí presentado no ha sido sometido previamente para la obtención de ningún grado académico o título profesional en esta u otra institución.

Asimismo, certificamos que todas las fuentes bibliográficas, documentos, materiales y recursos utilizados durante la elaboración de esta tesis han sido debidamente citados conforme a las normas académicas vigentes.
Nos comprometemos a que cualquier omisión, error o falta de cumplimiento en relación con la integridad académica es de nuestra entera responsabilidad.
Agradecimientos
Nelson duarte:
Quiero expresar mi profundo agradecimiento a todas las personas que me acompañaron durante este proceso y que hicieron posible la realización de esta tesis.
En primer lugar, agradezco a Dios, por darme la fortaleza, la claridad y la perseverancia necesarias para superar cada desafío que se presentó en el camino. Sin Su guía, este logro no habría sido posible.
A mi familia, gracias por su apoyo incondicional, por creer en mí incluso en los momentos en que dudé, y por ser siempre mi base emocional. Cada palabra de ánimo y cada gesto de cariño fueron fundamentales para mantenerme enfocado y motivado.
A mi novia, gracias por tu paciencia, tu amor y tu compañía en los momentos más intensos de este proceso. Tu apoyo constante fue una fuente de tranquilidad y motivación para seguir avanzando.


Declaración de autoría	3
Agradecimientos	3
I. Introducción	5
II. Identificación del Problema	6
2.1. Actualización y justificación del problema	6
2.1.1. Descripción de la organización.	6
2.1.2. Diagnóstico de la situación actual.	7
2.1.3. Descripción del problema.	9
2.2. Justificación del problema.	10
2.2.1. Relevancia del problema.	10
2.2.2. Complejidad del problema.	10
III. Levantamiento de Requerimientos	11
3.1 Determinación de los instrumentos a utilizar.	11
a) Observación directa en contexto real.	12
b) Entrevistas semi–estructuradas con actores reales.	12
c) Prototipado experimental iterativo.	13
3.2 Detalle de los requerimientos.	14
REQUERIMIENTOS FUNCIONALES (RF)	14
REQUERIMIENTOS NO FUNCIONALES (RNF)	16
3.3 Casos de uso.	16
CU01 — Registro físico por retiro	16
CU02 — Reposición física de stock	17
CU03 — Venta desde plataforma	17
CU04 — Reposición manual	18
CU05 — Generación de alerta	18
CU06 — Gestión de usuarios	18
CU07 — Análisis IA contextual	19
3.4 Diagramas de caso de uso.	19
IV. Marco Teórico	19
4.1. Investigación Bibliográfica	19
a) Gestión de inventarios	20
b) Sistemas de información	20
c) Automatización operativa	21
4.2. Internet de las Cosas (IoT)	21
4.3. Sensores de carga (Load cells)	22
4.4. Conversión digital (ADC – HX711)	22
4.5. Microcontroladores y MicroPython	23
4.6. Bases de datos en la nube	23
Supabase (PostgreSQL)	23
4.7. RBAC — Control basado en roles	24
4.8. Auditoría operativa	24
V. Objetivos del Proyecto	25
5.1. Solución tecnológica	25
5.1.1. Formulación de la solución	25
5.1.2. Herramientas de desarrollo	26
5.1.3. Alcance y restricciones	26
5.2. Impacto de la solución	27
5.2.1. Proceso de negocio afectado	27
5.2.2. Registro de interesados	27
5.2.3. Indicadores de gestión	28
5.2.4. Niveles de servicio	28
5.2.5. Respuestas ante fallas	28
5.3. Objetivos del proyecto	28
5.3.1. Objetivo general	29
5.3.2. Objetivos específicos	29
VI. Metodología de Trabajo (Scrumban real)	29
6.1. Metodología de desarrollo	30
6.1.1. Diagnóstico y análisis de la problemática	30
6.1.2. Definición de requerimientos y diseño técnico	30
6.1.3. Planificación del proyecto	31
6.1.4. Verificación y validación	32
6.1.5. Despliegue	33
6.1.6. Mantenimiento y mejoras	33
6.2. Duración y cronograma	34
6.3. Equipo de trabajo	35
6.4. Plan de recursos	35
VII. Definición de arquitectura TI	36
7.1. Tipo de arquitectura requerida	36
7.2. Componentes principales de la solución	37
1. Hardware IoT — Captura del fenómeno físico	37
2. Red y transporte de datos	38
3. Persistencia — Base de datos en la nube	38
4. Backend — Lógica de negocio	39
5. Frontend — Visualización operativa	40
6. Auditoría y IA contextual	40
7.3. Diagrama de arquitectura	41
VIII. Reconocimiento de arquitectura empresarial	41
8.1. Tipo y estructura organizacional objetivo	42
IX. Detalle de las Tecnologías a implementar	43
9.1. Análisis cualitativo y cuantitativo de tecnologías	43
1. Sensores de carga (Load Cells)	43
2. Conversor analógico–digital HX711	44
3. Microcontrolador Raspberry Pi Pico W	44
4. Plataforma de datos: Supabase (PostgreSQL)	45
5. Backend: Flask (Python)	46
6. Frontend: HTML + Jinja + Tailwind + JavaScript	47
7. Auditoría y mensajes IA contextual	47
9.2. Herramientas, lenguajes y componentes	48
X. Detalle de la Arquitectura	49
10.1. Diagrama BPMN del proceso	49
10.2. Diagramas de caso de uso	50
10.3. Diagrama de componentes	51
10.4. Modelo de Datos	51
10.5. Topología de comunicaciones	52
10.6. Diagrama de infraestructura	52
10.7. Diagrama de arquitectura	53
XI. Implementación de KPI y SLA	54
11.1. KPIs definidos	54
KPI 1 — Diferencia entre stock físico y stock digital (Δ Inventario)	54
KPI 2 — Tiempo de detección de evento físico	54
KPI 3 — Porcentaje de movimientos automáticos vs manuales	55
KPI 4 — Frecuencia de alertas válidas (precisión del sistema)	55
KPI 5 — Tiempo invertido en inventarios manuales	56
KPI 6 — Número de eventos sin responsable	56
11.2. Niveles de servicio (SLA)	56
SLA 1 — Disponibilidad del sistema	56
SLA 2 — Latencia lectura → registro	56
SLA 3 — Persistencia y auditoría	57
SLA 4 — Integridad del dato	57
SLA 5 — Tolerancia a fallo IoT	58
XII. Plan de Pruebas y Aseguramiento de Calidad	58
12.1. Plan de Pruebas	58
a) Pruebas de hardware IoT	58
b) Pruebas del backend	59
c) Pruebas de base de datos	60
d) Pruebas de interfaz	60
12.2. Normas y estándares	61
XIII. Plan de Implementación	62
13.1. Gestión de disponibilidad	62
a) Disponibilidad operacional	62
b) Reducción de puntos críticos	62
c) Supervisión del nodo IoT	62
13.2. Gestión de continuidad	63
a) Fallas del sensor o microcontrolador	63
b) Fallas de red	63
c) Actualizaciones	63
13.3. Plan de mantención	64
a) Mantención IoT	64
b) Mantención de software	64
c) Actualización operativa	65
XIV. Ajustes del Cronograma	65
14.1. Revisión de la carta Gantt	65
14.2. Ajustes principales realizados	67
a) Ajustes derivados del hardware IoT	67
b) Ajustes en el backend Flask	67
c) Ajustes en base de datos	68
d) Ajustes en frontend	69
14.3. Impacto de los ajustes	70
14.4. Lecciones derivadas de los ajustes	71
XV. Conclusiones	72
XVI. Referencias bibliográficas	73
XVII. Anexos	74

I. Introducción
La gestión de inventario constituye un eje crítico en la operación de pequeñas y medianas empresas. En sectores como las farmacias, bodegas de insumos o tiendas minoristas, la disponibilidad de productos no solo afecta la continuidad operativa, sino también la percepción del cliente, la seguridad de la cadena de suministro y la sostenibilidad del negocio. A diferencia de grandes organizaciones que operan con ERP industriales y sistemas automatizados, la mayoría de las PYMES chilenas funciona mediante procesos manuales o semiautomáticos: registros tardíos, conteos periódicos, planillas y software básico que solo muestra información una vez que el problema ya ocurrió.
Esta brecha operativa se traduce en inconsistencias entre el inventario físico y el digital, reposiciones tardías, quiebres de stock, pérdidas por merma y ausencia de trazabilidad real sobre quién, cuándo y cómo manipula los productos. El resultado no es solo una mala experiencia para el cliente; es pérdida económica directa, aumento de costos operativos y decisiones basadas en suposiciones, no en datos confiables.
En este contexto surge Weigence, un sistema inteligente de gestión de inventario diseñado para pequeñas y medianas organizaciones, cuyo objetivo es reemplazar el paradigma reactivo por uno preventivo y automatizado. La propuesta combina hardware IoT de bajo costo, servicios en la nube y una plataforma web modular capaz de transformar variaciones físicas de peso en información operativa útil. La premisa central es simple: cuando un producto se retira o se añade a un estante, el sistema debe saberlo sin depender de que un usuario lo ingrese manualmente.
El núcleo del proyecto se fundamenta en un prototipo físico compuesto por una celda de carga, un módulo HX711 y un microcontrolador Raspberry Pi Pico W, encargado de medir y digitalizar el peso en tiempo real. Cada variación registrada se envía a Supabase (PostgreSQL), donde los datos se almacenan, gestionan y posteriormente son procesados por el backend desarrollado en Python y Flask. Sobre esta arquitectura descansa una plataforma web construida con HTML, Tailwind CSS y JavaScript, que presenta módulos operativos clave: dashboard, inventario, movimientos, alertas, ventas, auditoría y gestión de usuarios.
El sistema no se limita a mostrar datos. Weigence incorpora una capa de asistencia inteligente orientada a apoyar la toma de decisiones. Esta inteligencia opera en dos niveles: mensajes breves, contextuales y directos en el encabezado de cada pantalla, y recomendaciones más extensas en el módulo de auditoría. Ambas funciones analizan el comportamiento real del inventario a partir de patrones visibles: inactividad prolongada, retiros no registrados, alertas consecutivas o movimientos irregulares. No se busca reemplazar al usuario ni tomar decisiones por él; se busca reducir la incertidumbre operativa y anticipar situaciones críticas antes de que afecten al negocio.
El proyecto se desarrolla con un enfoque práctico y de bajo costo. No pretende competir con soluciones corporativas ni con sistemas industriales complejos; su valor reside en su capacidad de adaptarse a la realidad de una PYME, donde el tiempo es limitado, el personal varía y la mayoría de los errores se producen por omisiones simples. La arquitectura planteada —IoT → Nube → Backend Flask → Frontend Web → Auditoría → IA contextual— permite escalar físicamente (multiplicando sensores y estantes) y lógicamente (más módulos, reportes, sucursales o integraciones futuras), sin afectar el diseño central.
Weigence presenta así una propuesta tecnológica concreta: automatizar el inventario, reducir la dependencia del criterio humano y ofrecer un sistema modular, accesible y técnicamente sustentable. El presente documento describe el proceso completo: desde la identificación del problema, el levantamiento de requerimientos y la definición de arquitectura, hasta la implementación funcional, pruebas, evaluación operativa y consideraciones éticas. El resultado no es un ejercicio teórico, sino una solución aplicada que demuestra que la automatización real puede implementarse incluso en los entornos más modestos.

II. Identificación del Problema
2.1. Actualización y justificación del problema
2.1.1. Descripción de la organización.
Las organizaciones objetivo del proyecto Weigence corresponden a bodegas pequeñas y medianas relacionadas con rubros de comercio minorista como farmacias, ferreterías, tiendas especializadas o negocios locales. Estas organizaciones comparten un patrón estructural: alta rotación de productos, tiempos operativos limitados y ausencia de personal exclusivo para la gestión de inventarios. Normalmente cuentan con entre uno y cinco trabajadores, donde cada uno cumple múltiples funciones simultáneas: venta, reposición, recepción de mercadería y atención a clientes.
Este tipo de empresa concentra sus esfuerzos en mantener flujo de ventas y continuidad operativa inmediata. Los procesos administrativos y de control suelen realizarse cuando el tiempo lo permite, y no como una actividad sistemática o planificada. La gestión de stock no es un proceso continuo, sino “eventual”: se revisa cuando algo falta, cuando un cliente reclama, o durante cierres periódicos. En la práctica, el inventario se convierte en un problema reactivo y no en un elemento estratégico.
La infraestructura tecnológica de estas bodegas usualmente consiste en un punto de venta simple o software comercial básico. Estas soluciones solo registran lo que el operador ingresa manualmente. No existe un mecanismo automático que contraste el inventario físico con el inventario del sistema. El dato digital es una promesa del usuario, no una verificación de la realidad. El sistema cree lo que el humano declara, aunque sea incorrecto, incompleto o tardío.
Este contexto describe organizaciones que operan a pulso, con conocimiento tácito, hábitos y memoria, sin apoyo de tecnologías avanzadas. El error humano no es un evento excepcional; es parte inherente del funcionamiento. Bajo estas condiciones, cada decisión se sustenta en percepciones, no en datos confiables. Weigence se formula como un sistema pensado para este escenario real, no idealizado: inventario dinámico, recursos limitados y necesidad urgente de automatización simple.
2.1.2. Diagnóstico de la situación actual.
El diagnóstico surge de observación operativa, entrevistas con encargados y pruebas experimentales con prototipos. Se identificaron cinco patrones que se repiten casi de manera sistemática en bodegas pequeñas y medianas:
1. El inventario es reactivo, no preventivo.
 Los datos de stock se revisan cuando surge un problema:
Se agota un producto inesperadamente.


Se reciben reclamos de clientes.


Se descubre una caja vacía en la vitrina.


El cierre contable no coincide con los registros.


La revisión no anticipa: corrige. Un sistema que opera bajo corrección constante acumula errores con el tiempo.
2. El stock digital y el stock físico nunca coinciden de forma total.
 El sistema puede estimar que hay 15 unidades, pero en el estante solo quedan 7.
 No hay mecanismos que detecten ese desajuste hasta que explota el problema.
 “El inventario siempre está un poco mal” fue una frase recurrente en entrevistas.
3. El proceso está fragmentado en múltiples microacciones no registradas.
Ejemplos reales:
“Saqué una unidad para dejarla en mostrador.”


“Vendí rápido y la anoto después.”


“Revisé stock y moví productos entre estantes.”


“Le di una caja a la persona que repone.”


Cada una de esas acciones sí afecta el inventario, pero no siempre se registra.
 No existe auditoría continua ni estímulo para registrar exactamente todo.
4. La trazabilidad es inexistente.
 Nadie sabe quién movió qué y cuándo.
 Cuando el stock no cuadra, se asigna culpa a:
error humano,


robo hormiga,


proveedores,


“fallas del sistema”.
 Pero nunca se llega a una explicación objetiva, porque no hay datos operativos directos.


5. Los inventarios manuales consumen recursos y destruyen productividad.
 Para “corregir” el sistema, los trabajadores pasan horas contando productos que ya se vendieron, que se perdieron o que nunca fueron registrados.
 Durante ese proceso:
la venta se detiene,


el personal deja otras funciones,


el negocio pierde continuidad operativa.


Este diagnóstico muestra un patrón simple pero consistente: las PYME no fallan porque sean irresponsables o incapaces; fallan porque dependen totalmente del humano en un sistema que exige precisión constante.
2.1.3. Descripción del problema.
El problema que aborda Weigence se puede formular así:
Las bodegas pequeñas y medianas no cuentan con un mecanismo automatizado que valide el inventario físico en tiempo real, lo que genera diferencias permanentes entre el stock real y el registrado, impactando la continuidad operativa, la toma de decisiones y la rentabilidad.
Este problema no es abstracto: se manifiesta en situaciones concretas y frecuentes.
Escenario típico 1:
 El sistema de ventas indica que hay stock disponible.
 Un cliente solicita un producto.
 El trabajador va al estante: no hay unidades.
 El sistema “mintió”. El cliente se va.
Escenario típico 2:
 Se realizan compras preventivas basadas en intuición (“esto se mueve harto”).
 Luego se descubre que había stock suficiente, pero el sistema estaba mal actualizado.
 Resultado: inmovilización de capital, sobreinventario y espacio utilizado innecesariamente.
Escenario típico 3:
 Se detectan faltantes, pero no se puede identificar su origen.
¿Fue robo?


¿Fue una venta no registrada?


¿Fue reposición tardía?


¿Fue un movimiento interno?
 No hay datos. Solo especulación.


Escenario típico 4:
 Los inventarios físicos se postergan porque son tediosos y costosos en tiempo.
 Cuando se hacen, revelan desequilibrios acumulados que ya no se pueden explicar.
En síntesis, el problema no es que “faltan productos”.
 El problema es que la organización no tiene un espejo confiable de la realidad.
 El sistema digital está desconectado del mundo físico y depende de la voluntad humana para mantenerse sincronizado.
2.2. Justificación del problema.
2.2.1. Relevancia del problema.
Impacto económico directo.
 Cada unidad no registrada o perdida representa dinero que la organización jamás recupera.
 Una bodega pequeña no compensa esas pérdidas con volumen.
 Cualquier merma erosiona el margen, y en negocios con rotación irregular, ese margen ya es reducido.
Impacto comercial.
 Cuando un producto aparece como disponible y no lo está, se genera desconfianza.
 Un cliente que experimenta esto en farmacia o ferretería percibe desorden:
 “Si no saben cuántos productos tienen, ¿qué tan serios son?”
Impacto en operación.
 El inventario manual y los ajustes a último minuto son trabajo duplicado.
 El operador atiende clientes, mueve productos y registra datos.
 La carga cognitiva aumenta y la probabilidad de error también.
Impacto estratégico.
 Una empresa sin datos reales no puede tomar decisiones racionales.
 Compra cuando no debe, deja de comprar cuando necesita, pierde ventas y no lo sabe.
 El negocio vive en incertidumbre operativa crónica.
2.2.2. Complejidad del problema.
El problema no es “hacer un software”.
 El problema real es la naturaleza humana + la imprevisibilidad operativa + el costo.
Humano:
 La gente no tiene tiempo para registrar cada movimiento.
 No es incompetencia: es realidad.


Operativo:
 Los productos se mueven en unidades pequeñas, arbitrarias, sin patrón constante.
 No es logística corporativa; es caótico y rápido.


Económico:
 Las PYME no pueden pagar sistemas industriales RFID, machine learning avanzado o hardware especializado de $1.500.000 por estante.
 Weigence debe funcionar con tecnología accesible, simple y replicable.


En este contexto, la solución adecuada no es controlar al operador,
 sino eliminar el punto de fallo:
 automatizar la detección física del inventario y auditar los eventos en tiempo real.

III. Levantamiento de Requerimientos
El levantamiento de requerimientos constituye una fase crítica en el diseño de sistemas informáticos, particularmente en soluciones que integran hardware IoT, servicios en la nube y plataformas web. En el caso de Weigence, esta etapa fue determinante para trazar límites claros entre lo que la tecnología puede hacer y lo que la operación de una bodega realmente necesita.
A diferencia de proyectos puramente software, donde el modelo puede refinarse en iteraciones de código, en sistemas IoT cada requerimiento tiene implicancias físicas, económicas y operativas. La lectura de una celda de carga no existe como idea abstracta; existe como señal eléctrica que fluctúa con ruido, humedad, magnetismo, vibración y movimiento humano. Por este motivo, el levantamiento se abordó desde una perspectiva operacional y experimental, no solo documental.
3.1 Determinación de los instrumentos a utilizar.
Para capturar los requerimientos funcionales y no funcionales del sistema se emplearon tres instrumentos principales: observación directa, entrevistas con actores clave y experimentación iterativa con prototipo IoT.
a) Observación directa en contexto real.
La observación operativa se realizó sobre el funcionamiento cotidiano de bodegas reales, identificando cómo se realiza el inventario en la práctica. Los hallazgos no se basaron en manuales ni protocolos formales, sino en decisiones día a día:
Se repone producto cuando el estante “se ve vacío”.


Se retira producto para ventas rápidas sin registro inmediato.


Se dejan cajas “a un lado” sin ingresar el movimiento.


Se hacen notas escritas en papel con intención de ingresarlas más tarde.


Los registros manuales se postergan por sobrecarga de tareas.


Estas observaciones permitieron comprender que el sistema debía adaptarse al caos controlado de la operación, no exigir que la operación se adapte al sistema.
b) Entrevistas semi–estructuradas con actores reales.
Las entrevistas se realizaron con dueños de negocios, supervisores y operadores.
 Las preguntas se centraron en tres ejes:
Cómo perciben el inventario.


“Veo cuánto queda y me acuerdo”.


“Lo revisamos cuando faltan cosas”.


Cuándo registran movimientos.


“Cuando tenemos tiempo”.


“Cuando el sistema lo pide”.


“A veces después de vender”.


Qué entienden como problema.


“Que falten cosas sin explicación”.


“Que el sistema diga algo distinto”.


“Que tengamos que contar todo de nuevo”.


Las respuestas fueron consistentes:
 La información digital depende del comportamiento humano, no del proceso real.
c) Prototipado experimental iterativo.
Un prototipo funcional se implementó en hardware real:
Celda de carga 1kg


HX711 (conversor ADC 24 bits)


Raspberry Pi Pico W


MicroPython para lectura


Supabase como nube de almacenamiento


Backend Flask


Interfaz web


La fase experimental reveló fenómenos que no aparecen en documentación técnica:
Variaciones de peso por vibración humana.


Doble lectura cuando el objeto toca primero un borde.


“Efecto memoria” del sensor post-cambio de carga.


Latencia perceptible entre envío WiFi y escritura DB.


Lecturas espurias cuando la fuente USB no está estabilizada.


Estos descubrimientos no surgen leyendo Wikipedia.
 Surgen usando el sistema como lo usaría un humano.
 Por eso, el levantamiento no fue “qué queremos que el sistema haga”, sino
 qué necesita hacer para sobrevivir al mundo real.

3.2 Detalle de los requerimientos.
Los requerimientos se agruparon en funcionales y no funcionales.
 Se redactaron en lenguaje operativo, no académico, siendo tan específicos como fuera necesario para el desarrollo real.

REQUERIMIENTOS FUNCIONALES (RF)
RF1. Detección automática de cambios de peso.
 El sistema debe detectar incrementos o decrementos sin intervención del usuario.
RF2. Registro del evento físico en la base de datos.
 Cada cambio debe transformarse en un evento almacenado como:
fecha/hora


peso previo


peso nuevo


diferencia calculada


estante asociado


RF3. Actualización automática de stock.
 La cantidad estimada debe ajustarse según el peso detectado y la unidad de medida del producto.
RF4. Registro manual complementario.
 El usuario debe poder ingresar movimientos manualmente (ingreso, salida, reposición) sin bloquear la lectura automática.
RF5. Alertas operativas.
 El sistema debe generar alertas bajo criterios:
stock bajo


cambios bruscos


actividad anormal


inactividad prolongada


RF6. Auditoría histórica.
 El sistema debe conservar un historial completo:
qué pasó


cuándo pasó


quién lo provocó (manual)


por qué se disparó (algoritmo)


RF7. Gestión de usuarios con RBAC.
 Roles:
Administrador (control total)


Supervisor/Jefe (lectura extendida + informes)


Operador (movimientos + ventas sin gestión de usuarios)


RF8. Módulo Ventas.
 Las ventas deben asociarse a movimientos físicos de stock.
RF9. Dashboard operativo.
 El usuario debe visualizar el estado general del sistema sin navegar múltiples pantallas.
RF10. Mensajería IA contextual.
 Mensajes breves en header y análisis más extensos en auditoría.

REQUERIMIENTOS NO FUNCIONALES (RNF)
RNF1. Rendimiento.
 La lectura del sensor → actualización sistema ≤ 3 s.
RNF2. Usabilidad.
 Diseño minimalista y entendible para usuarios no técnicos.
RNF3. Confiabilidad.
 Las lecturas deben filtrarse para evitar falsas detecciones.
RNF4. Seguridad.
 Contraseñas cifradas, rutas protegidas y permisos según rol.
RNF5. Escalabilidad física.
 Debe permitir múltiples sensores y estantes sin rediseño arquitectónico.
RNF6. Compatibilidad.
 Acceso vía navegador estándar, sin instalación local.
RNF7. Auditabilidad.
 Cada evento debe registrarse de forma consultable y verificable.

3.3 Casos de uso.
Los casos de uso se redactan en lenguaje natural, centrados en acciones humanas y eventos físicos.
CU01 — Registro físico por retiro
Actor: Operador / Estante
 Flujo:
El operador retira un producto.


La celda detecta pérdida de peso.


Raspberry envía lectura.


Backend identifica variación.


Sistema registra movimiento automático.


Auditoría crea evento.


Dashboard refleja nuevo stock.


CU02 — Reposición física de stock
Actor: Operador / Estante
 Flujo:
El operador añade producto al estante.


La celda registra aumento de peso.


Backend calcula unidades equivalentes.


Sistema actualiza stock.


No requiere registro manual.


CU03 — Venta desde plataforma
Actor: Operador
Operador registra venta.


Sistema descuenta stock asociado.


Auditoría muestra evento “venta registrada”.


Si el peso no coincide posteriormente → alerta.

CU04 — Reposición manual
Actor: Operador
El operador repone pero decide registrar manualmente.


Sistema genera movimiento “reposición manual”.


Auditoría conserva responsable.


CU05 — Generación de alerta
Sensor detecta stock bajo.


Backend dispara evento.


Se notifica visualmente al usuario.


Auditoría crea registro formal.



CU06 — Gestión de usuarios
Actor: Administrador
Crea o modifica cuenta.


Asigna Rol.


El sistema restringe accesos según permiso.



CU07 — Análisis IA contextual
Actor: Plataforma
El sistema detecta anomalías operativas.


Genera mensaje breve (header).


Elabora análisis extenso (auditoría IA).


3.4 Diagramas de caso de uso.
Modulo Inventario:


Modulo movimientos:

Modulo alertas:



Usuarios:



Auditoria:


IV. Marco Teórico
El marco teórico del proyecto Weigence se construye sobre los fundamentos que sustentan su diseño tecnológico y operativo: gestión de inventarios, sistemas de información, arquitectura IoT, sensorización por peso (load cells), procesamiento digital mediante ADC, bases de datos en la nube, modelos de control de acceso y auditoría operativa.
 Su función no es rellenar el documento, sino alimentar el razonamiento técnico que justifica cada decisión del proyecto.
4.1. Investigación Bibliográfica
La investigación bibliográfica se orientó a identificar teorías, modelos y tecnologías directamente relacionadas con la automatización de inventarios y el uso de sensores en soluciones accesibles para PYMES. El enfoque fue deductivo: comprender cómo se gestiona inventario hoy, qué técnicas se usan a nivel industrial, por qué no se adoptan en escalas menores y qué alternativas técnicas existen.
a) Gestión de inventarios
La gestión de inventarios se define como el conjunto de procesos que permiten mantener el equilibrio entre disponibilidad de productos y demanda operativa.
 Las metodologías tradicionales proponen modelos como:
EOQ (Economic Order Quantity):
 intenta determinar el punto óptimo entre costo de almacenamiento y costo de compra.


Punto de Reorden (ROP):
 establece una cantidad mínima a la que se dispara una acción de reposición.


First-In/First-Out (FIFO):
 controla la rotación priorizando la salida de los productos más antiguos.


Estos modelos son eficaces solo cuando el dato base es confiable.
 En organizaciones pequeñas, el problema no es “calcular”, sino “saber cuántas unidades hay realmente”.
 Sin ese dato, cualquier modelo es inútil, porque el inventario digital es ficción.
b) Sistemas de información
Los sistemas de información combinan tres ejes: personas, procesos y tecnología.
 El error habitual en bodegas pequeñas es asumir que basta con tecnología.
 La realidad es otra:
Si el sistema exige que el humano introduzca cada movimiento,


y el humano no lo hace por carga de trabajo, estrés o costumbre,


entonces el sistema no funciona.


El sistema, en la práctica, está sometido a la fricción humana.
 Weigence elimina este cuello de botella:
 no pregunta “cuántos productos hay”, sino que lo detecta físicamente.
c) Automatización operativa
La automatización no significa eliminar al humano, sino reducir dependencia de su disciplina.
 En bodegas pequeñas, el inventario falla no por falta de conocimiento, sino por dinámica operativa:
60 segundos para atender un cliente.


30 segundos para vender.


15 segundos para entregar producto.


“Registrar movimiento” entra último en prioridades.
 La automatización convierte una operación que requiere atención humana en un evento autónomo.
4.2. Internet de las Cosas (IoT)
IoT (Internet of Things) propone conectar dispositivos físicos a sistemas digitales mediante sensores, protocolos de comunicación y servicios remotos.
 En el caso de Weigence, la cadena es directa:
Sensor → Microcontrolador → Red → Base de datos → Sistema Web
No hay decisiones mágicas.
 No hay machine learning futurista.
 Hay máquinas observando un fenómeno físico y reportándolo.
En entornos de pequeña escala, IoT aporta tres ventajas:
Medición continua.
 El dato no depende de la voluntad del usuario.


Neutralidad.
 El sensor no “olvida” ni “miente”.


Contextualización.
 Los eventos pueden correlacionarse con acciones humanas.


4.3. Sensores de carga (Load cells)
Las celdas de carga son transductores capaces de convertir fuerzas mecánicas en señales eléctricas.
 En aplicaciones de inventario, permiten medir cambios de peso asociados a ingreso o retiro de producto.
 Las más comunes para sistemas comerciales son single point load cells, diseñadas para cargas de 1 a 20 kg.
Características relevantes para Weigence:
Alta resolución → pequeñas variaciones detectables.


Lectura analógica → requiere digitalización.


Sensibilidad a vibración y temperatura → exige filtrado.


Esto implica que el sensor no entrega un “número mágico”:
 genera ruido, deriva y microfluctuaciones.
 Weigence tuvo que domesticar el dato, no solo leerlo.
4.4. Conversión digital (ADC – HX711)
El módulo HX711 convierte señales analógicas en digitales con una resolución de 24 bits.
 Esta resolución es crítica:
 permite detectar movimientos pequeños, como retirar una caja de paracetamol o un paquete de tornillos.
Conceptos clave:
Ganancia seleccionable (32–64–128): amplifica la señal de la celda.


Ruido inherente: requiere promedios, filtros y ventanas temporales.


Drift térmico: cambios leves con temperatura ambiente.


En la práctica, leer el peso “real” implica:
Calibración inicial con referencia conocida.


Estabilización temporal antes de considerar el evento.


Conversión a unidades operativas (peso bruto → unidades reales).


Nada de esto aparece en tutoriales básicos.
 Se aprende probando.
4.5. Microcontroladores y MicroPython
Un microcontrolador no es un computador personal.
 Tiene memoria limitada, reloj de ejecución modesto y carece de sistema operativo.
 Su ventaja es que no muere bajo carga, no se congela como un navegador, y opera en tiempo real.
Raspberry Pi Pico W fue elegido por razones contundentes:
Soporta MicroPython → curva de aprendizaje reducida.


WiFi integrado → elimina módulos extra.


Bajo consumo → unidades operativas 24/7.


Precio accesible → escalamiento por estante viable.


El microcontrolador ejecuta la tarea más simple y necesaria: leer, filtrar y enviar.
4.6. Bases de datos en la nube
Supabase (PostgreSQL)
Supabase es plataforma basada en PostgreSQL con servicios REST integrados.
 Ventajas críticas para PYME:
Sin servidores propios.


API generada automáticamente.


RLS (Row Level Security).


Escalamiento gradual.


Un punto clave:
 los datos de hardware no se guardan en planilla Excel.
 Se almacenan de forma estructurada, trazable y consulta inmediata.
4.7. RBAC — Control basado en roles
El control basado en roles (RBAC) es estándar de seguridad organizacional:
 cada usuario accede a funciones según su responsabilidad.
Weigence aplica:
Administrador: control total.


Supervisor/Jefe: visión y análisis.


Operador: operaciones básicas.


No todos son iguales frente al inventario.
 El sistema lo reconoce.
4.8. Auditoría operativa
La auditoría no es un “historial”:
 es la memoria del sistema.
Sin auditoría:
no se puede evaluar errores,


no se puede asignar responsabilidades,


no se puede aprender del pasado.


Weigence no elimina el error humano, lo ilumina.
 Registra:
Eventos


Causas


Usuario (si aplica)


Contexto


Esto convierte el inventario en proceso verificable y no en una discusión.


V. Objetivos del Proyecto
Los objetivos del proyecto Weigence se establecieron a partir del problema operativo identificado en bodegas pequeñas y medianas: la ausencia de un mecanismo automático que sincronice el inventario real con el sistema digital. Los objetivos priorizan funcionalidad real por sobre complejidad técnica, buscan reducir la dependencia de la disciplina humana y entregar una plataforma que soporte decisiones operativas.
5.1. Solución tecnológica
La solución propuesta consiste en un sistema de inventario basado en sensores IoT que detecta variaciones de peso y transforma estos cambios físicos en registros operativos. El objetivo no es construir un sistema futurista ni experimental, sino uno usado día a día en una operación real, con mínima fricción para el usuario.
5.1.1. Formulación de la solución
Weigence se implementa como una arquitectura distribuida simple y eficiente:
IoT (sensor → microcontrolador) que captura eventos físicos.


Plataforma en la nube (Supabase) para almacenamiento y consistencia.


Backend Flask para procesamiento, lógica de negocio y modularidad.


Frontend web para visualización operativa amigable.


Auditoría e IA contextual, para decisiones informadas.


El sistema se concibe como una herramienta que “escucha” el estante: si el producto entra o sale, el sistema lo detecta. Esto libera al usuario del registro manual y evita que el inventario dependa exclusivamente de su atención.
5.1.2. Herramientas de desarrollo
Las tecnologías seleccionadas se justifican por equilibrio entre costo, facilidad de mantenimiento y escalabilidad real:
Raspberry Pi Pico W: bajo costo, WiFi integrado, MicroPython.


HX711 + load cell: lectura de peso con alta resolución.


Supabase / PostgreSQL: estructura robusta con seguridad a nivel de filas.


Flask + Python: microservicio modular, rápido de mantener.


HTML + Jinja2 + Tailwind + JS: interfaz limpia, sin sobrecarga.


Las herramientas no buscan “mostrar conocimiento”, sino resolver el problema con recursos accesibles para una PYME.
5.1.3. Alcance y restricciones
Alcance:
Registro físico automático de inventario.


Módulo de movimientos (entrada / retiro).


Alertas operativas.


Auditoría completa de eventos.


Gestión de usuarios con roles.


Fuera de alcance:
Machine Learning avanzado.


Integración con ERP corporativos.


Sistemas RFID industriales.


Multi–bodega en etapa inicial.


Weigence prioriza un Producto Mínimo Viable realista, no una simulación académica.
5.2. Impacto de la solución
5.2.1. Proceso de negocio afectado
El sistema afecta directamente el proceso central de la bodega: control de stock y reposición.
 Actualmente dependiente del operador, pasa a depender de lecturas automatizadas.
 Esto transforma un proceso manual, propenso a error, en un ciclo continuo de monitoreo.
5.2.2. Registro de interesados
Los interesados principales son:
Dueños o administradores de PYME: buscan control y reducción de pérdidas.


Supervisores: necesitan análisis para decidir compras y reposición.


Operadores: requieren una herramienta simple que no agrande su carga.


Todos comparten un factor común: no tienen tiempo para contar productos.
5.2.3. Indicadores de gestión
Los indicadores clave que se buscan mejorar:
Tasa de quiebres de stock.


Diferencia entre stock físico y digital.


Tiempo invertido en inventarios manuales.


Unidades perdidas por merma no explicada.


Son indicadores medibles que afectan decisiones y rentabilidad.
5.2.4. Niveles de servicio
El proyecto define niveles de servicio realistas:
La plataforma debe responder en tiempos aceptables (dashboard funcional, actualización rápida sin recargar la página).


La lectura físico → digital debe ejecutarse en segundos.


Las alertas deben informarse sin que el usuario recorra múltiples pantallas.


5.2.5. Respuestas ante fallas
Weigence asume el mundo real.
 Si el sensor se desconecta, el sistema:
Registra evento de falla.


Notifica al usuario.


Permite operación manual temporal.


El sistema no “se cae”; vuelve al modo humano, garantizando continuidad.
5.3. Objetivos del proyecto
5.3.1. Objetivo general
Diseñar y desarrollar un sistema integral de gestión de inventarios para bodegas pequeñas y medianas, capaz de automatizar la detección de movimientos de stock mediante sensores IoT, almacenando y procesando los datos en una plataforma web con módulos operativos, auditoría y control por roles.
5.3.2. Objetivos específicos
Implementar un prototipo IoT funcional (celda de carga + HX711 + Raspberry Pico W) que detecte variaciones reales de peso.


Desarrollar un backend modular en Flask capaz de procesar lecturas, registrar movimientos y exponer servicios a la interfaz.


Diseñar un frontend claro y accesible, orientado al uso cotidiano y no a usuarios técnicos.


Incorporar auditoría operativa, registrando eventos críticos, manuales y automáticos.


Establecer control de acceso por roles (RBAC) para proteger funciones según perfil.


Generar mensajes asociados a comportamiento operativo, priorizando IA contextual sobre modelos predictivos complejos.

VI. Metodología de Trabajo (Scrumban real)
El desarrollo de Weigence se abordó utilizando SCRUMBAN, una metodología híbrida entre Scrum y Kanban adecuada para proyectos donde existe incertidumbre tecnológica (IoT, calibraciones, ruido de sensores, tiempos de hardware) y, al mismo tiempo, se requieren entregas constantes y tangibles.
 La elección no fue teórica: surgió de la necesidad práctica.
 Scrum puro exige sprint planificados con backlog cerrado, lo cual es difícil cuando no sabes si el sensor que hoy funciona seguirá estable mañana.
 Kanban puro no genera hitos ni priorización clara, lo que complica las etapas de entrega que exige el proyecto de título.
 Scrumban permite combinar ambas lógicas: flujo continuo + metas periódicas + control visual del avance + flexibilidad técnica.
6.1. Metodología de desarrollo
La metodología se aplicó a través de seis fases. Cada fase no fue lineal; se revisó y reajustó según resultados reales del prototipo.
6.1.1. Diagnóstico y análisis de la problemática
Se inició el proyecto identificando cómo operan las bodegas en la realidad, evitando suposiciones.
 Durante esta fase se realizaron:
Observaciones operativas.


Conversaciones con encargados.


Pruebas manuales de conteo y reposición.


Validaciones de cómo se comporta el inventario en días de alta y baja demanda.


Este proceso permitió comprender que el problema no es solo tecnológico:
 es una mezcla entre comportamiento humano, presión operativa y falta de herramientas.
 La solución debía acomodarse a esa realidad, no intentar cambiarla.
6.1.2. Definición de requerimientos y diseño técnico
Con el problema claro, se definieron requerimientos funcionales y no funcionales.
 Se validaron los siguientes criterios:
El sistema no debe pedirle al usuario más esfuerzo del que hace hoy.


La automatización debe operar en segundo plano.


Toda señal física debe generar un evento digital.


La interfaz debe ser entendible sin capacitación.


El diseño técnico se estableció pensando en un MVP realista, no un producto final corporativo.
 Esto implicó:
Arquitectura IoT → nube → backend → frontend.


División clara entre captura automática y registro manual.


Auditoría transversal a todo evento.


No se plantearon ideas futuristas como machine learning predictivo o visión artificial.
 El foco: resolver el problema hoy.
6.1.3. Planificación del proyecto
Se estructuraron tareas siguiendo tableros Kanban:
To Do → pendientes


In Progress → en desarrollo


Review/Testing → revisión y pruebas


Done → completadas


Las tareas se definieron por módulos:
Hardware IoT


Backend Flask


Base de datos


Interfaz web


Auditoría


Roles y permisos


Alertas


Prototipo físico


Cada módulo tenía subtareas concretas y medibles, por ejemplo:
calibración de la celda


configuración de HX711


envío MQTT/HTTP


persistencia en Supabase


renderizado de dashboard


lógica de movimientos


validación de permisos por rol


Mientras Scrum pide historias de usuario cerradas,
 Scrumban permite que esas historias se ajusten en tiempo real según resultados del sensor.
6.1.4. Verificación y validación
La verificación se realizó sobre el desempeño técnico:
¿El sensor detecta el cambio?


¿La lectura llega a Supabase?


¿El backend procesa correctamente?


¿El frontend lo refleja?


¿Se genera auditoría asociada?


La validación fue operacional:
¿Este flujo ayuda al operador o lo molesta?


¿La alerta es útil o solo ruido?


¿La UI confunde o acelera el trabajo?


Ejemplo real:
Durante las pruebas, movimientos de peso se repetían por vibraciones mínimas.
 La solución no fue “corregir después”, fue agregar filtro temporal y umbrales mínimos.
La metodología requirió corregir en el origen, no a nivel visual.
6.1.5. Despliegue
El despliegue de Weigence se planteó por capas:
Firmware del microcontrolador


Backend en Flask


Frontend y recursos estáticos


Base de datos y cambios de esquema


Cada despliegue debía:
No afectar datos históricos.


Mantener operación manual disponible como fallback.


Ser reversible sin destruir el entorno.


6.1.6. Mantenimiento y mejoras
El mantenimiento se abordó como iteraciones graduales:
Calibraciones periódicas del sensor.


Ajustes a la interfaz según feedback del usuario.


Correcciones en auditoría para reducir ruido.


Ajustes en la sensibilidad de alertas.


Inclusión de nuevos módulos solo cuando existe necesidad real.


No se desarrollaron características “decorativas”.
 Cada mejora debe justificar su existencia con datos.
6.2. Duración y cronograma
El cronograma se estructuró en un plano modular y no en un único flujo lineal.
 La base fue Scrumban: tareas flexibles, pero con hitos claros.
 Los hitos principales fueron:
Prototipo IoT funcional (lectura estable).


Persistencia en Supabase.


Backend operativo.


Módulo inventario.


Movimientos automáticos.


Alertas iniciales.


Auditoría.


Gestión RBAC.


Pruebas completas.


Cada fase avanzó sin bloquear a las otras.
 Ejemplo: mientras se afinaba la calibración del sensor, se implementaba el dashboard y la gestión de usuarios.
6.3. Equipo de trabajo
Se conformó un equipo pequeño con roles complementarios:
Diseño UI / Desarrollo Frontend / Integración


Marketing y levantamiento de requerimientos (encuestas)


Recursos humanos, normativa y programación


El equipo no siguió jerarquías rígidas.
 Las decisiones se tomaron en función del avance real y la capacidad individual.
Ejemplo:
Si el sensor no respondía, todos se enfocaban en resolverlo.
 Un frontend bonito no sirve si el hardware no detecta producto.
6.4. Plan de recursos
El plan de recursos contempló:
Hardware IoT: sensor single-point, HX711, Raspberry Pi Pico W.


Infraestructura web: Supabase.


Herramientas de desarrollo: VSCode, GitHub.


Servidor backend: entorno Python con Flask.


Dominio, SSL y eventual hosting.


Mano de obra técnica del equipo.


Los recursos se escogieron bajo criterio PYME:
accesibles,


mantenibles sin especialistas,


escalables por adición gradual,


fáciles de reemplazar.


VII. Definición de arquitectura TI
La arquitectura tecnológica de Weigence se definió con un enfoque pragmático: resolver el problema operacional del inventario minimizando dependencias humanas, utilizando hardware accesible y servicios escalables.
 La arquitectura no nace como un diseño corporativo, sino desde el punto de vista de una PYME que debe operar con costos acotados, mantenimiento bajo y facilidad de reemplazo.
 Cada componente de la arquitectura responde a un objetivo funcional concreto.
7.1. Tipo de arquitectura requerida
Weigence se implementa mediante una arquitectura descentralizada por captura y centralizada por gestión, donde la detección de eventos físicos se realiza en el borde (edge IoT), pero la interpretación, persistencia y visualización se gestionan desde la nube.
En términos simples:
El estante detecta → La nube almacena → El backend procesa → El frontend muestra → La auditoría registra.
Este modelo evita que la operación dependa de infraestructura local costosa o servidores dedicados.
 La carga de trabajo se distribuye de forma lógica:
IoT: captura del dato físico.


Nube / DB: registro y persistencia consistente.


Backend: reglas operativas, API y validaciones.


Frontend: visualización e interacción humana.


Auditoría: trazabilidad.


IA contextual: interpretación de patrones.


El sistema se compone de capas interconectadas pero débilmente acopladas, lo que permite modificar un módulo sin desarmar el resto.
7.2. Componentes principales de la solución
La arquitectura incluye seis niveles funcionales:
1. Hardware IoT — Captura del fenómeno físico
Raspberry Pi Pico W + HX711 + celda de carga
El sensor convierte fuerza mecánica en señal analógica.


HX711 digitaliza con resolución de 24 bits.


El microcontrolador filtra ruido temporal.


Los datos se envían mediante WiFi.


Decisiones clave:
MicroPython para simplicidad y velocidad de desarrollo.


Tolerancia a fallos: si el sensor deja de enviar, la operación sigue manual.


El hardware no ejecuta lógica compleja:
Solo reporta la realidad.
 No calcula stock, no genera reportes, no manipula lógica.
Eso evita errores y reduce carga computacional.
2. Red y transporte de datos
El envío se realiza mediante conexión WiFi local hacia Internet.
 No se utiliza MQTT ni brokers complejos porque los costos operativos y técnicos no son justificables para el alcance del proyecto.
 Se emplean peticiones HTTP o endpoints REST hacia el backend.
Ventajas:
Baja fricción de implementación.


Fácil depuración.


Compatible con entornos de PyME (router doméstico).


3. Persistencia — Base de datos en la nube
Supabase + PostgreSQL
Modelos principales:
productos


pesajes / lecturas


movimientos


estantes


usuarios


ventas


detalle_ventas


alertas


auditoría


mensajes IA


Características relevantes:
Row Level Security (RLS) para controlar accesos.


API autogenerada REST para minimizar backend repetitivo.


Almacenamiento centralizado para consultas y reportes.


Supabase evita infraestructura propia y permite escalar con el negocio.
4. Backend — Lógica de negocio
Flask (Python)
El backend actúa como capa de interpretación entre el mundo físico y la operación humana.
Responsabilidades:
Convertir lectura bruta en unidades operativas.


Determinar si un cambio es ingreso o retiro.


Registrar movimientos automáticos y manuales.


Generar alertas.


Servir endpoints al frontend.


Validar permisos por rol (RBAC).


El backend no asume tareas innecesarias como predicciones o cálculos complejos:
 Su rol es intermediario confiable entre datos y decisiones.
Arquitectura interna:
Rutas modulares (dashboard, inventario, movimientos, auditoría, usuarios).


Funciones especializadas por dominio.


Servicios auxiliares (IA contextual, filtros, utilidades).


5. Frontend — Visualización operativa
HTML + Tailwind CSS + Jinja + JavaScript
Principios de diseño:
No saturar con dashboards cargados.


Mostrar información útil, inmediata y entendible.


Reducir clics; priorizar flujo visual.


El frontend se orienta a:
Proveer una “visión de estado” rápida.


Permitir acciones básicas sin complejidad.


Comunicar alertas sin interrumpir.


Un operador no lee manuales de 40 páginas.
 El sistema debe “decirle” lo necesario para trabajar.
6. Auditoría y IA contextual
La auditoría registra todo evento:
tarea manual,


detección automática,


alerta,


anomalía,


login.


Weigence no usa IA predictiva; usa IA contextual:
Mensajes breves en encabezado.


Análisis operativos explicativos en auditoría.


La IA no toma decisiones por el usuario:
Le explica el contexto y lo alerta.
Esto evita la sensación de “caja negra”.
7.3. Diagrama de arquitectura
La plantilla exige diagramas.
 Aquí solo indico los espacios donde van:
(IMAGEN: Arquitectura IoT → Nube → Backend Flask → Frontend → Auditoría → IA Contextual)
Sugerencias para el diagrama:
Celda → HX711 → Raspberry Pi Pico W → Endpoint Flask → DB Supabase


Frontend consumiendo API → Módulos (Inventario, Movimientos, Alertas, Auditoría)


Capa transversal IA y Auditoría

VIII. Reconocimiento de arquitectura empresarial
La arquitectura empresarial de Weigence se concibe para encajar en organizaciones pequeñas y medianas que no cuentan con departamentos tecnológicos formales ni procesos de gestión altamente estructurados. En estas empresas, la toma de decisiones se concentra en uno o dos actores —dueño o administrador—, mientras que las tareas operativas son ejecutadas por personal multifunción. Por lo tanto, el sistema no puede imponer jerarquías o burocracia: debe acompañar la dinámica natural de la bodega.
En este contexto, Weigence se integra como un subsistema de soporte operativo, no como una plataforma centralizadora que sustituya otros procesos. Su propósito es eliminar el punto ciego entre inventario físico y digital, entregando una representación objetiva del estado real del stock.
8.1. Tipo y estructura organizacional objetivo
Las organizaciones a las cuales apunta Weigence comparten características esenciales:
Estructura horizontal: no existen áreas robustas de TI, logística o supply chain.


Roles mezclados: quien vende también repone, mueve productos o hace cierres.


Poca capacidad de supervisión: no hay tiempo para auditorías continuas.


Procesos ad-hoc: decisiones reactivas según urgencias del día.


Este entorno determina que la arquitectura TI del sistema debe cumplir tres condiciones prácticas:
Bajo costo.
 Weigence no está pensado para empresas que pueden pagar sensores industriales de 10–15 millones.
 Debe ser accesible en hardware y mantenimiento.


Baja dependencia de especialistas.
 La instalación y operación no puede depender de ingenieros dedicados.
 Un usuario con nociones básicas debe poder operar el sistema.


Convergencia operativa mínima.
 El flujo del negocio no se debe rediseñar para “calzar” con el software.
 El sistema debe adaptarse a la forma en que la bodega trabaja.


Desde la perspectiva de arquitectura empresarial, Weigence se posiciona como un componente tecnológico modular que agrega visibilidad y control, sin alterar los procesos comerciales existentes ni introducir capas administrativas innecesarias.
 A diferencia de ERPs corporativos o sistemas contables, Weigence no intenta controlar a la organización: solo mide lo que realmente ocurre.

IX. Detalle de las Tecnologías a implementar
La selección tecnológica de Weigence responde a criterios funcionales y operativos propios de un entorno PYME: bajo costo, escalabilidad gradual, facilidad de mantenimiento y estabilidad en operación continua.
 Cada componente fue elegido para cumplir un rol específico dentro de la arquitectura: captura física, procesamiento, almacenamiento, visualización y verificación.
9.1. Análisis cualitativo y cuantitativo de tecnologías
1. Sensores de carga (Load Cells)
Tecnología seleccionada: celda de carga tipo single-point.
 Aplicación: detectar variaciones de peso asociadas al ingreso o retiro de productos.
Ventajas cualitativas:
Sencillez conceptual: el sensor mide un fenómeno físico directo.


Neutralidad operativa: no requiere interacción humana.


Exactitud práctica: detecta cambios pequeños (gramos).


Ventajas cuantitativas:
Capacidad nominal: 1–10 kg por estante (según versión).


Resolución efectiva: superior a métodos manuales.


Costo unitario bajo.


Razonamiento: en una farmacia o ferretería el producto no “tiene GPS”.
 Su existencia se manifiesta en masa.
 La celda convierte esa realidad física en información usable.
2. Conversor analógico–digital HX711
Tecnología: HX711, ADC 24 bits.
 Rol: digitalizar la señal analógica de la celda.
Razones para elegirlo:
Amplificación integrada (ganancias 32/64/128).


Ruido aceptable en entornos reales.


Consumo eléctrico mínimo.


Ecosistema bien documentado.


Alternativas descartadas:
ADC genéricos 10–12 bits → insuficientes para detectar cambios pequeños.


Módulos industriales → costo 10–20 veces mayor sin beneficio proporcional.


3. Microcontrolador Raspberry Pi Pico W
Rol: adquisición de datos y envío hacia la nube.
Ventajas concretas:
WiFi integrado → no requiere módulos externos.


Programación en MicroPython → curva rápida, alta legibilidad.


Estabilidad 24/7 → diseñado para sistemas embebidos.


Costo por unidad bajo → escalamiento viable por estante.


Por qué no Arduino UNO / Nano:
Ausencia de WiFi nativo.


Manejo menos eficiente de operaciones en segundo plano.


Requiere adaptadores o shields adicionales.


Por qué no Raspberry Pi 4 como nodo sensor:
Consumo mayor.


Overkill técnico: un computador completo para leer un ADC.


Conclusión: el Pico W hace exactamente lo que se necesita y nada más.
4. Plataforma de datos: Supabase (PostgreSQL)
Rol: almacenamiento estructurado y seguro.
Motivos seleccionados:
Modelo relacional robusto.


API REST autogenerada.


RLS (Row Level Security) para control granular por usuario.


Escalabilidad gradual (plan gratuito → pro).



Comparación con alternativas:
Alternativa
Razón descartada
MySQL local
Requiere servidor dedicado, mantenimiento y backup manual
Firebase Firestore
Modelo no relacional confuso para inventarios físicos
MongoDB Atlas
Poco natural para auditoría y relaciones cruzadas
Planillas tipo Google Sheets
No hay integridad ni transacciones

La lógica de inventario exige consistencia transaccional:
 movimiento → auditoría → alerta → impacto en stock.
 Esto es PostgreSQL, no planillas.
5. Backend: Flask (Python)
Rol: puente entre el mundo físico (lecturas) y el mundo humano (operación).
Ventajas:
Microframework → modularidad natural.


Bajo overhead.


Integración directa con Python (ciencia, IA contextual, cálculos).


Rutas claras (Blueprints).


Por qué no Django:
Sobredimensionado para un MVP.


Estructura rígida que agrega complejidad sin beneficio real.


Requiere capas adicionales para API REST.


Por qué no Node/Express:
Ecosistema más complejo para tratamiento numérico y sensores.


Python ya domina el stack IoT y procesamiento.


Weigence no necesita un “backend poderoso”.
 Necesita un backend disciplinado y entendible.
6. Frontend: HTML + Jinja + Tailwind + JavaScript
Principio de diseño: claridad antes de estética compleja.
HTML: simplicidad y compatibilidad universal.


Jinja2: render del lado servidor, evita sobrecargar al cliente.


Tailwind: diseño rápido, consistente, sin CSS repetitivo.


JS: interactividad puntual; no Single Page Application.


Por qué no React/Vue/Angular:
Incrementan mantenimiento.


Forman barrera de entrada para operadores sin soporte técnico.


Aumentan complejidad por solo mostrar tablas y gráficos.


Una bodega no es Spotify.
 El frontend debe decir qué hay y qué falta, sin distracciones.
7. Auditoría y mensajes IA contextual
Tipo de IA seleccionado: contextual, basada en reglas y patrones simples.
Rol real:
Detectar anomalías operativas (inactividad, patrones raros).


Explicar al usuario “qué está pasando” en lenguaje natural.


No inventar predicciones.


Ejemplo simple:
“Inactividad acumulada de 27 h en Estante A. Último movimiento: 04/11.”
No es un modelo de machine learning.
 Es inteligencia aplicada: el sistema interpreta señales y las traduce en insights.
Una PYME no necesita una “IA para impresionar evaluadores”.
 Necesita un sistema que hable claro.
9.2. Herramientas, lenguajes y componentes
Hardware:
Load cell single-point (1–10 kg).


HX711.


Raspberry Pi Pico W.


Firmware:
MicroPython (lectura, filtrado, envío).


Backend:
Flask + Python (rutas modulares).


Librerías auxiliares: requests, seguridad, filtrado.


Base de datos:
Supabase (PostgreSQL + RLS).


Frontend:
HTML + Tailwind CSS.


Jinja2.


JavaScript.


Colaboración:
GitHub (repositorios, ramas).


VSCode + Live Share.


Ambiente:
Hosting Supabase.


Dominio + SSL (implementación productiva).


X. Detalle de la Arquitectura
La arquitectura de Weigence se diseñó para que el sistema funcione como un flujo continuo de datos: la información nace en un sensor físico, viaja a través de un microcontrolador, se almacena en la nube, se procesa en el backend y finalmente se presenta al usuario mediante una plataforma web. Esta arquitectura no se concibe desde la teoría, sino desde la operación cotidiana de una bodega real con recursos limitados, personal multifuncional y permanentes cambios en su inventario.
10.1. Diagrama BPMN del proceso
(IMAGEN: diagrama BPMN del flujo de entrada/salida de productos)
Descripción del proceso:
El diagrama BPMN representa el ciclo de reposición y retiro de productos, separando claramente las acciones humanas de los eventos automatizados. El objetivo es demostrar cómo el sistema elimina tareas manuales innecesarias y convierte acciones físicas en información confiable.
Flujo conceptual:
Acción física: el operador retira o adiciona un producto al estante.


Evento IoT: la celda detecta una variación de peso.


Procesamiento local: Raspberry Pico W filtra ruido y genera dato estable.


Transmisión: el dato se envía al backend.


Interpretación: Flask determina si el cambio corresponde a entrada o salida.


Persistencia: Supabase registra el movimiento y actualiza el stock.


Notificación: interfaz muestra el cambio y, si corresponde, genera alerta.


Auditoría: cada evento queda registrado con sello temporal.


Este BPMN permite justificar por qué el sistema no depende del usuario para capturar variaciones reales del inventario.
10.2. Diagramas de caso de uso
(IMAGEN: diagrama de caso de uso — Inventario y Movimientos)
 (IMAGEN: diagrama de caso de uso — Alertas y Auditoría)
 (IMAGEN: diagrama de caso de uso — Gestión de Usuarios)
Explicación:
Los diagramas de caso de uso representan cómo los distintos roles interactúan con el sistema:
Operador: realiza ventas, movimientos manuales, consulta stock.


Supervisor/Jefe: analiza datos, revisa histórico de movimientos, revisa alertas.


Administrador: gestiona usuarios, permisos y configuraciones.


Los sensores no aparecen como “actores humanos”, sino como actores del sistema. La arquitectura de Weigence reconoce que la fuente primaria de la verdad es el hardware, no la entrada manual.
10.3. Diagrama de componentes
(IMAGEN: diagrama de componentes — IoT, Backend, Base de Datos, Frontend, Auditoría)
Descripción funcional:
Componente IoT: Raspberry Pico W + HX711 + load cell.
 Captura y digitaliza cambios de peso.


Componente Backend Flask:
 Interpreta lecturas, ejecuta lógica operativa, calcula unidades y aplica RBAC.


Base de datos (Supabase/PostgreSQL):
 Persistencia de productos, lecturas, movimientos, usuarios, auditoría y mensajes IA.


Frontend Web:
 Representación visual organizada en módulos (Dashboard, Inventario, Movimientos, Ventas, Alertas, Auditoría).


Capa Transversal IA Contextual:
 Analiza patrones y comunica recomendaciones o advertencias.


Cada componente tiene responsabilidades bien definidas y evita sobrecargas innecesarias.
10.4. Modelo de Datos
(IMAGEN: modelo entidad-relación — productos, estantes, movimientos, usuarios, auditoría, alertas, ventas, detalle_ventas)
Descripción de las entidades clave:
productos: información base (nombre, peso unitario, código, categoría).


estantes: ubicación física y carga asociada.


pesajes/lecturas: lecturas de sensores con valor bruto, fecha y estante.


movimientos: registros derivados de eventos físicos o manuales.


usuarios: RUT, nombre, correo, rol.


ventas: registro de transacciones.


detalle_ventas: productos y cantidades asociados a cada venta.


alertas: eventos críticos disparados por reglas.


auditoría: registro detallado de acciones, anomalías, logins y eventos.


El modelo evita tablas redundantes y privilegia relaciones claras y comprobables.
10.5. Topología de comunicaciones
(IMAGEN: topología de comunicaciones — nodo IoT → backend → DB → interfaz)
Flujo de datos:
El microcontrolador envía lecturas mediante conexión WiFi.


El backend recibe la petición y aplica interpretación.


Los datos se almacenan en Supabase mediante API.


El frontend consulta o recibe cambios según el contexto.


La topología es cliente-ligero → servidor → nube.
 Esto es crítico: el hardware jamás depende de una red interna compleja ni servidores locales.
10.6. Diagrama de infraestructura
(IMAGEN: infraestructura — Raspberry en estante, Internet, Supabase, Backend, Usuarios)
Descripción realista:
Nivel físico: 1 estante con celda de carga + Raspberry Pico W.


Nivel de red: router local común (PYME estándar).


Nivel nube: Supabase (DB + API).


Nivel aplicación: backend Flask alojado en entorno cloud.


Nivel usuario: navegador (Chrome, Firefox, Edge).


No se requiere hardware especial, microservidores ni racks industriales.
10.7. Diagrama de arquitectura
(IMAGEN: arquitectura IoT → nube → backend Flask → frontend → auditoría → IA)
Resumen conceptual:
IoT (Edge): mide el fenómeno real.


Nube: mantiene integridad de datos y persistencia.


Backend Flask: transforma señal → información.


Frontend: muestra contexto y acciones.


Auditoría: registra decisiones.


IA contextual: interpretaciones y recomendaciones.


La arquitectura está diseñada para escalar por sencillez:
 más estantes = más Raspberry + sensores, no más complejidad estructural.

XI. Implementación de KPI y SLA
La evaluación del desempeño de Weigence no puede basarse únicamente en percepciones subjetivas o satisfacción visual del usuario. El sistema automatiza procesos, por lo que debe medirse bajo indicadores concretos que reflejen el impacto operativo y económico. Los KPI seleccionados responden directamente al problema identificado: diferencias entre inventario físico y digital, tiempos operativos y ocurrencia de eventos no registrados. Los SLA, por su parte, definen el nivel de servicio que el sistema debe garantizar para operar de manera confiable en un ambiente PYME.
11.1. KPIs definidos
Los KPIs se seleccionaron bajo cuatro criterios: medibles, comparables, consistentes en el tiempo y relevantes para la toma de decisiones. No se eligieron indicadores “decorativos” o académicamente atractivos, sino métricas que afectan directamente la operación de una bodega.
KPI 1 — Diferencia entre stock físico y stock digital (Δ Inventario)
Objetivo: Reducir la brecha entre inventario real medido por sensor y el inventario registrado manual o por ventas.
Fórmula:
Δ = |Stock físico – Stock sistema|
Meta realista: Δ → 0
 No es utópico: un sistema automático debe revelar diferencias como excepciones, no como norma.
Interpretación:
 Si el sistema vive con diferencias, no controla nada, solo expone números.
KPI 2 — Tiempo de detección de evento físico
Objetivo: Medir cuántos segundos transcurren entre la acción real y el reflejo digital.
Fórmula:
t = timestamp_evento_físico – timestamp_registro
Meta operativa: ≤ 3–5 s
Esto es defendible:
El sensor lee en ms.


El envío tarda ~1–2 s.


El backend procesa rápido.


La interfaz refleja cambio en el próximo refresh/consulta.


Impacto real:
 Si el sistema detecta tarde, el operador deja de confiar en él.
KPI 3 — Porcentaje de movimientos automáticos vs manuales
Objetivo: Evaluar efectividad de la automatización.
Fórmula:
Mov.Automáticos / Total de Movimientos * 100
Meta inicial (MVP): ≥ 60%
 Meta post–ajuste: ≥ 80%
Una PYME no va a registrar todo manualmente.
 El objetivo es que el sistema registre la mayoría de los eventos y el humano complemente.
KPI 4 — Frecuencia de alertas válidas (precisión del sistema)
Objetivo: El sistema debe alertar cuando existe un problema real, no de manera aleatoria.
Indicador práctico:
Alertas válidas / Alertas generadas
Meta: ≥ 70–80%
Punto clave:
 Un sistema que molesta es un sistema que se desinstala.
KPI 5 — Tiempo invertido en inventarios manuales
Afecta directamente la productividad.
Medición:
Antes de Weigence → horas de conteo.


Con Weigence → solo revisión por anomalías.


Meta: reducción ≥ 50%
Este KPI es entendible por cualquier dueño: menos tiempo = menos costos.
KPI 6 — Número de eventos sin responsable
Esto refleja el caos real de la operación.
Regla:
Todo movimiento manual debe tener responsable.
 Todo movimiento automático debe quedar auditado.
Meta: ≤ 5% de eventos sin responsable.
Si el número crece, el sistema no está trazando correctamente.
11.2. Niveles de servicio (SLA)
Los SLA definen compromisos mínimos que el sistema debe cumplir para ser útil.
 No son promesas “perfectas”: son metas razonables.
SLA 1 — Disponibilidad del sistema
Objetivo: Que la plataforma sea accesible para operar la bodega.
Meta MVP: 95–97%
 Meta escalada: 99%
SLA 2 — Latencia lectura → registro
Es uno de los pilares técnicos del proyecto.
Meta realista: ≤ 3 s desde el cambio físico.
No es marketing, es física:
Pico W transmite,


backend procesa,


DB escribe,


UI refleja.


Si se extiende a 10–15 s, el usuario deja de confiar en los sensores.
SLA 3 — Persistencia y auditoría
Todo movimiento se debe registrar.
Si el sensor falla:
Se registra un evento de fallo.


Se habilita registro manual.


Promesa mínima:
100% de eventos generan una entrada en auditoría (física, manual o de sistema).
SLA 4 — Integridad del dato
No se aceptan cambios sin timestamp.


No se aceptan movimientos sin origen (físico o manual).


Los registros deben poder trazarse hasta el usuario o sensor.


Este SLA es el que te salva en defensa oral:
“El sistema no discute, solo registra lo que pasa.”
SLA 5 — Tolerancia a fallo IoT
No existe bodega perfecta ni WiFi perfecto.
Regla operacional:
Si el sensor se desconecta → operación manual permanece disponible.
Meta:
Tiempo sin sistema IoT no debe afectar ventas ni reposición.
XII. Plan de Pruebas y Aseguramiento de Calidad
La calidad del sistema Weigence se evaluó mediante un plan de pruebas orientado a validar el funcionamiento del hardware IoT, la consistencia del backend, la confiabilidad de la base de datos y la usabilidad de la interfaz. El objetivo principal fue asegurar que los eventos físicos capturados por los sensores se reflejen correctamente en el sistema digital, manteniendo trazabilidad completa y reduciendo la intervención manual.
Las pruebas se ejecutaron en fases y abarcaron tres dimensiones: pruebas funcionales, pruebas técnicas y pruebas operativas. Cada dimensión se diseñó considerando el entorno real de uso de una bodega, donde existen ruido físico, limitaciones de red y múltiples acciones simultáneas por parte del usuario.
12.1. Plan de Pruebas
a) Pruebas de hardware IoT
Objetivo: validar que el sensor de peso detecta variaciones reales y que el microcontrolador transmite datos estables sin pérdidas.
Casos de prueba:
CP01: Colocar peso conocido en el estante (por ejemplo, 120 g) y verificar lectura digital.


CP02: Retirar parcialmente un producto y medir caída gradual del peso.


CP03: Retirar un producto completo y confirmar detección única y estable.


CP04: Estímulo de vibración suave (movimiento de mano) para verificar filtrado.


CP05: Reinicio eléctrico del microcontrolador y reconexión automática a WiFi.


Criterios de aceptación:
El sistema debe registrar una sola variación por evento físico.


La señal debe estabilizarse antes de generar un movimiento.


Las variaciones sin efecto real (vibraciones o posicionamiento) no deben ser registradas.


b) Pruebas del backend
Objetivo: garantizar que el backend interprete correctamente los datos provenientes del IoT, aplique reglas de negocio y mantenga consistencia.
Casos de prueba:
CP06: Recepción de lectura válida → registro automático de movimiento.


CP07: Lectura inferior al umbral configurado → ignorar evento.


CP08: Lectura mayor al peso de una unidad → registrar como ingreso.


CP09: Fallo de sensor → generación de evento y registro en auditoría.


CP10: Intento de acceso a endpoint sin autenticación → rechazo por RBAC.


Criterios de aceptación:
Las unidades asociadas a cada lectura deben ser consistentes con el peso unitario del producto.


Los fallos deben generar eventos informativos sin detener el sistema.


c) Pruebas de base de datos
Objetivo: validar integridad de datos y comportamiento de las tablas ante diferentes escenarios.
Casos:
CP11: Inserción de movimiento automático → creación de registro en tabla “movimientos”.


CP12: Inserción de movimiento manual → registro con responsable.


CP13: Registro de alerta por stock bajo → entrada en tabla “alertas”.


CP14: Registro de login → entrada en tabla “auditoría”.


Criterios de aceptación:
No deben existir registros sin timestamp.


No deben existir movimientos sin referencia al estante o producto.


Los registros manuales deben estar asociados a un usuario válido.


d) Pruebas de interfaz
Objetivo: comprobar que el usuario accede a la información de forma clara y sin fricciones.
Casos:
CP15: Visualización de dashboard con estado de inventario actualizado.


CP16: Acceso a historial de movimientos.


CP17: Consulta de alertas activas y detalle de cada evento.


CP18: Gestión de usuarios según rol asignado.


Criterios de aceptación:
La interfaz debe reflejar cambios sin confusión visual.


Los elementos críticos (alertas, stock bajo) deben ser visibles sin navegar múltiples páginas.


Los usuarios deben ver únicamente las funciones disponibles para su rol.


12.2. Normas y estándares
Weigence adopta buenas prácticas aplicables al desarrollo de software e integración IoT, asegurando que el sistema sea mantenible y verificable a largo plazo.
Registro de eventos: cada operación debe generar un registro auditable.


Consistencia transaccional: los movimientos deben ejecutarse en orden atómico; si falla un componente, no se debe perder información.


Validación de datos: las lecturas deben ser filtradas antes de generar acciones.


Seguridad por rol: acceso restringido mediante RBAC, evitando acciones no autorizadas.


Disponibilidad operativa: el sistema debe conservar funcionalidad manual ante fallos del sensor.


Rastreabilidad: toda interacción debe poder identificarse por timestamp y usuario.


Estas normas permiten argumentar que el sistema cumple criterios básicos de confiabilidad, incluso en ambientes no técnicos.


XIII. Plan de Implementación
l plan de implementación de Weigence establece los pasos necesarios para desplegar el sistema en un entorno real de bodega pequeña o mediana. Este plan no se plantea como una instalación corporativa, sino como un proceso progresivo y controlado, basado en la integración paulatina de sensores, configuración de la plataforma y validación de la operación. La implementación prioriza continuidad, simplicidad y reversibilidad: el sistema puede funcionar en modo manual ante fallas del IoT y no requiere infraestructura compleja.
13.1. Gestión de disponibilidad
La gestión de disponibilidad se basa en asegurar que el sistema permanezca utilizable incluso en escenarios donde alguna parte de la arquitectura falle.
a) Disponibilidad operacional
El sistema debe garantizar que el usuario pueda consultar inventario, revisar alertas y registrar movimientos aunque el nodo IoT no esté operativo. Esto asegura que la bodega continúe sus operaciones sin interrupción.
Medidas aplicadas:
Lecturas de sensores desacopladas de la interfaz.


Módulo de movimiento manual disponible en todo momento.


Persistencia centralizada en Supabase para evitar pérdida de datos locales.


b) Reducción de puntos críticos
La arquitectura elimina dependencias innecesarias.
 No existe un servidor local cuya caída paralice el sistema.
 El backend y la base de datos en la nube permiten continuidad desde cualquier dispositivo.
c) Supervisión del nodo IoT
En caso de falla de hardware:
Se registra evento en auditoría.


Se mantiene modo manual.


La operación se conserva hasta reponer el dispositivo.


De esta forma, la disponibilidad no depende de la perfección del sensor, sino de la flexibilidad del sistema.
13.2. Gestión de continuidad
La continuidad asegura que el sistema siga funcionando de manera estable ante eventos previsibles (cortes de red, reinicios, fallas puntuales del microcontrolador o la API).
a) Fallas del sensor o microcontrolador
Si la Raspberry Pico W deja de transmitir:
El sistema no detiene el backend ni bloquea la interfaz.


Se activa registro manual.


Se genera registro de evento para seguimiento.


b) Fallas de red
En entornos PYME la conectividad puede ser irregular.
 La continuidad se garantiza mediante:
Reintentos de envío desde el firmware.


Reconexión automática del nodo.


Backend tolerante a solicitudes repetidas.


c) Actualizaciones
Las actualizaciones deben:
Ser incrementales.


No modificar datos históricos.


Mantener estructura de tablas preexistentes.


No exigir reinstalación del firmware.


El sistema se actualiza por capas, sin detener la operación principal.
13.3. Plan de mantención
El mantenimiento de Weigence no se basa en ciclos complejos, sino en ajustes regulares que permiten conservar la precisión y confiabilidad del sistema.
a) Mantención IoT
Recalibración periódica de la celda de carga.


Revisión del cableado y conectores.


Sustitución del microcontrolador en caso de falla prolongada.


La mantención se realiza en tiempos no operativos, idealmente fuera de horario comercial.
b) Mantención de software
Validación de logs de auditoría.


Revisión de alertas falsas o excesivas para ajustar umbrales.


Actualización de dependencias del backend.


Corrección de detalles de interfaz según retroalimentación.


El mantenimiento software se realiza sin afectar registros históricos ni flujos activos.
c) Actualización operativa
En caso de agregar nuevos estantes o módulos:
Se instala un nuevo nodo IoT independiente.


Se vincula a un estante en la base de datos.


No se altera el diagrama general del sistema.


El sistema escala por adición, no por reemplazo.
XIV. Ajustes del Cronograma
Durante el desarrollo de Weigence, el cronograma original debió ser ajustado en múltiples ocasiones, principalmente debido a la complejidad derivada de la calibración del hardware IoT y a la integración entre los datos físicos capturados por el sensor y la estructura de datos en la plataforma web. Los ajustes no fueron improvisados: respondieron a evidencia técnica recogida durante el desarrollo y a dificultades concretas presentadas por el prototipo real.
La carta Gantt final se reorganizó en base a paquetes de trabajo (IoT, backend, base de datos, frontend y pruebas), con tareas más específicas, duraciones reales y responsables definidos. Esta revisión permitió reflejar avances verificables, identificar cuellos de botella y asegurar que la ruta crítica asociada al sensor y a la persistencia de datos fuera tratada con prioridad.

14.1. Revisión de la carta Gantt
La planificación inicial agrupaba tareas en bloques amplios (por ejemplo “desarrollo de frontend” o “pruebas del sensor”), lo cual resultó insuficiente para gestionar dependencias, identificar riesgos y evaluar carga real de trabajo. Por este motivo, la carta Gantt fue desglosada a un nivel operativo, incorporando actividades concretas y responsables.
Un ejemplo de este ajuste se observa en el paquete de trabajo “Integración IoT”:
Tarea
Duración estimada
Responsable
Predecesora
Instalación de firmware base en Raspberry Pico W
3 h
Paulo
—
Lecturas brutas del HX711
6 h
Francisco
Firmware instalado
Implementación de filtro simple por promedio
4 h
Francisco
Lecturas brutas
Calibración con pesos conocidos (100 g – 500 g – 1 kg)
8 h
Francisco
Filtro simple
Ajuste de umbrales (sensibilidad)
4 h
Francisco
Calibración
Testing de estabilidad por vibración
5 h
Equipo
Umbrales definidos
Envío de datos a backend vía HTTP
6 h
Paulo
Lecturas estables
Validación registro con Supabase
6 h
Nelson
Endpoint operativo

Este desglose permitió visualizar que varias actividades dependían de la estabilización física de la celda de carga, lo que desplazó tareas de backend y frontend hasta contar con datos confiables.

14.2. Ajustes principales realizados
a) Ajustes derivados del hardware IoT
Las pruebas de lectura bruta mostraron variaciones significativas en el peso detectado cuando se manipulaban productos o se movía el estante. El cronograma inicial consideraba “configuración del sensor” como una tarea única. En la práctica, se desglosó en:
Lectura bruta y gráfica de señal en consola.


Implementación de promedio móvil simple.


Ajuste de ventana de muestras.


Validación con cargas reales.


Registro de comportamiento frente a vibración.


Nuevo ajuste fino de umbrales.


Incremento del número de muestras antes de disparo de evento.


Cada uno de estos pasos añadió entre 4 y 8 horas adicionales al paquete IoT y desplazó tareas dependientes del backend.

b) Ajustes en el backend Flask
La primera versión del backend asumía que un cambio de peso correspondía directamente a un movimiento. Durante las pruebas se descubrió que:
cambios menores (< 4–5 g) no correspondían a eventos reales;


reposiciones parciales generaban múltiples lecturas consecutivas;


algunos movimientos eran “ruido” por reposición en la repisa.


Por lo anterior, se incorporaron nuevas tareas:
Tarea
Duración
Responsable
Normalización de datos de lectura
6 h
Francisco
Agrupación de eventos consecutivos
4 h
Paulo
Registro en tabla de auditoría
4 h
Nelson
Endpoint para consulta de movimientos
6 h
Francisco
Pruebas de ingreso ficticio
3 h
Equipo

Estos ajustes reordenaron el cronograma: el backend pasó a depender de la calidad de la lectura IoT, no de la interfaz.

c) Ajustes en base de datos
El diseño original del modelo contemplaba productos y movimientos. A medida que surgieron necesidades operativas se incorporaron:
Tabla “alertas”.


Registro de eventos automáticos vs manuales.


Trazabilidad por usuario o sensor.


Metadata de fallas y reconexión.


Ejemplo de tareas que se agregaron:
Tarea
Duración
Responsable
Creación tabla alertas
2 h
Paulo
Creación tabla auditoría
3 h
Nelson
Ajuste claves foráneas en movimientos
3 h
Francisco
Test de integridad referencial
4 h
Equipo

Estas modificaciones obligaron a desplazar tareas frontend que dependían de datos finales.

d) Ajustes en frontend
En el diseño inicial del sistema se priorizó la vista de inventario estático. Durante las pruebas surgió la necesidad de:
visualizar movimientos temporales,


exponer alertas con contexto,


diferenciar movimientos automáticos de manuales,


integrar trazabilidad desde auditoría.


Esto generó tareas nuevas como:
Tarea
Duración
Responsable
Componente historial de movimientos
8 h
Francisco
Vista de alertas
6 h
Paulo
Interfaz de auditoría
10 h
Nelson
Filtro de periodo en dashboard
4 h
Francisco


14.3. Impacto de los ajustes
Los ajustes realizados no representaron retrasos improductivos, sino aprendizaje técnico aplicado. Al desglosar las tareas y definir responsables:
La ruta crítica del proyecto quedó claramente asociada a la estabilización del sensor y a la interpretación de lecturas.


Se evitó que la interfaz avanzara con datos simulados.


La integración entre IoT–backend–DB se volvió un flujo verificable y auditable.


Las pruebas dejaron de ser un evento final y pasaron a integrarse dentro de cada paquete de trabajo.


La carta Gantt final representó el desarrollo real, no un plan hipotético.

14.4. Lecciones derivadas de los ajustes
Los ajustes del cronograma permitieron concluir que los proyectos basados en sensores físicos requieren planificaciones flexibles y iterativas. La estimación tradicional por “módulos de software” fue insuficiente; los tiempos reales los determinó la estabilidad del prototipo.
Entre las principales lecciones:
La calibración del sensor condiciona todo el sistema.
 No es una tarea menor: controla el backend, la base de datos y la interfaz.


Las tareas deben ser medibles y asignadas.
 Los paquetes amplios ocultan problemas; los responsables claros los revelan.


Los ajustes no son un fracaso, sino una adaptación.


XV. Conclusiones
El desarrollo de Weigence permitió abordar un problema recurrente en bodegas pequeñas y medianas: la falta de sincronía entre el inventario físico y el inventario digital. Los registros manuales, la ausencia de control constante y la dependencia de la memoria del operador generan diferencias de stock que derivan en pérdida de ventas, sobrestock o roturas de inventario. El proyecto demostró que la incorporación de sensores IoT y una plataforma web puede reducir significativamente estas brechas operativas mediante medición directa del estado real del producto en el estante.
La propuesta no consistió en reemplazar procesos humanos, sino en integrar herramientas tecnológicas simples para capturar información objetiva. Este enfoque permitió desplazar la carga de trabajo desde la revisión manual hacia la verificación de excepciones: el operador deja de contar productos y pasa a revisar alertas de movimientos y diferencias detectadas. Con ello, el inventario deja de ser un evento puntual y se transforma en un proceso continuo.
En términos de ingeniería, la solución evidenció que la estabilidad de un prototipo IoT no depende únicamente de la programación o del modelo de datos, sino de la calidad y comportamiento del sensor. La calibración, el filtrado de ruido y la interpretación de variaciones fueron tareas determinantes para que el sistema pudiera operar de forma confiable. La experiencia demostró que, en proyectos donde intervienen fenómenos físicos, la fase de diseño debe contemplar pruebas iterativas, tolerancia a fallos y mecanismos de validación real.
Asimismo, la integración con Supabase y Flask permitió asegurar trazabilidad y persistencia de datos sin requerir infraestructura compleja. La arquitectura modular facilitó la incorporación de funciones incrementales —como auditoría, alertas o historial de movimientos— sin afectar las bases del sistema. Esta estructura generó un entorno de desarrollo controlado, donde las funcionalidades evolucionaron a partir de necesidades observadas y no de presupuestos teóricos.
Desde el punto de vista operativo, el proyecto permitió validar que un sistema de automatización debe adaptarse a la dinámica del usuario. Las bodegas PYMES no funcionan de forma estructurada: las entradas y salidas son irregulares, los operadores rotan y los registros manuales suelen omitirse por presión del tiempo. Weigence se diseñó justamente para ese escenario, manteniendo opción manual ante fallos del sensor y privilegiando la continuidad operativa sobre el bloqueo del sistema. Esto permitió consolidar una plataforma tolerante y útil incluso en contextos con conectividad fluctuante.
Finalmente, el proceso de desarrollo evidenció el valor de una gestión flexible. El cronograma inicial fue reestructurado a medida que surgieron obstáculos técnicos, priorizando primero la estabilidad del sensor, luego la interpretación de datos y posteriormente la interfaz. Esta adaptación no fue un retroceso, sino un mecanismo necesario para construir una solución funcional y defendible en un entorno real.
Weigence no pretende ser un sistema para reemplazar a plataformas empresariales de alto costo, sino una herramienta pragmática orientada a bodegas pequeñas y medianas que necesitan visibilidad inmediata de su inventario. El proyecto demostró que una arquitectura IoT simple, combinada con un backend modular y una interfaz clara, puede entregar información útil y trazable sin exigir al usuario capacidades técnicas avanzadas.

XVI. Referencias bibliográficas
[1] Raspberry Pi Foundation.
 Raspberry Pi Pico W Product Brief.
 2022. Disponible en: https://datasheets.raspberrypi.com/picow/pico-w-product-brief.pdf
[2] SparkFun Electronics.
 Load Cell Amplifier HX711 — Hookup Guide & Datasheet.
 Disponible en: https://learn.sparkfun.com/tutorials/load-cell-amplifier-hx711-breakout-hookup-guide
[3] Geekcreit / Avia Semiconductor.
 HX711 — 24-bit ADC for Weigh Scales. Datasheet oficial.
 Disponible en: https://cdn.sparkfun.com/datasheets/Sensors/ForceFlex/hx711_english.pdf
[4] MicroPython Development Team.
 MicroPython Documentation.
 Disponible en: https://docs.micropython.org/en/latest/
[5] Raspberry Pi Foundation.
 Getting Started with MicroPython on Raspberry Pi Pico.
 Disponible en: https://www.raspberrypi.com/documentation/microcontrollers/micropython.html
[6] Supabase.
 Supabase Documentation — Postgres, Auth, REST.
 https://supabase.com/docs
[7] Pallets Projects.
 Flask Documentation (3.x).
 https://flask.palletsprojects.com/
[8] Tailwind Labs Inc.
Tailwind CSS Documentation.
https://tailwindcss.com/docs

[13] ISO/IEC 25010:2011.
Systems and software engineering — System and software quality models.
XVII. Anexos
Diagrama de componentes






Diagrama BPMN

