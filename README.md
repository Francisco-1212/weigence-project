# Weigence Project
**Sistema de Gestión de Inventario Inteligente (IoT + Web)**

Weigence es una plataforma diseñada para la automatización y control de stock en tiempo real. El proyecto resuelve la problemática de las discrepancias en inventarios físicos mediante la integración de hardware (sensores) y una infraestructura de software robusta.

## Tecnologías y Stack Técnico
* **Backend:** Python con Framework Flask.
* **Base de Datos:** PostgreSQL (Gestionada en Supabase).
* **Frontend:** Interfaz web desarrollada con HTML, CSS (Tailwind) y JavaScript.
* **Hardware/IoT:** Integración de sensores de carga para la digitalización de peso y stock.
* **Herramientas de Entorno:** Git, GitHub, VS Code y entorno Linux para despliegue.

## Arquitectura del Sistema
El proyecto implementa una arquitectura basada en el patrón **MVC (Modelo-Vista-Controlador)**:
1. **Capa de Datos:** Modelo relacional en PostgreSQL que asegura la integridad de los registros transaccionales.
2. **Capa Lógica:** Controladores en Python que procesan las señales de los sensores y gestionan la lógica de negocio.
3. **Capa de Presentación:** Panel web para la visualización de datos, historial de movimientos y gestión de alertas.



## Funcionalidades Principales
* **Monitoreo en Tiempo Real:** Actualización automática del stock sin intervención manual.
* **Detección de Diferencias:** Algoritmos para identificar inconsistencias entre el stock físico y el registrado.
* **Sistema de Alertas:** Notificaciones automáticas ante niveles bajos de productos o movimientos no autorizados.
* **Visualización de Datos:** Dashboard con gráficos históricos para el apoyo en la toma de decisiones operativas.

## Instalación y Ejecución
1. Clonar el repositorio:
   `git clone https://github.com/Francisco-1212/weigence-project.git`
2. Instalar dependencias:
   `pip install -r requirements.txt`
3. Configurar variables de entorno (.env) para la conexión a la base de datos.
4. Ejecutar la aplicación:
   `python app.py`

