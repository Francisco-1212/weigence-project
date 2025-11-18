"""
Sistema de logging centralizado para la aplicación
"""
import logging
import logging.handlers
import os
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """Formateador con colores para consola"""
    
    # Códigos de color ANSI
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Verde
        'WARNING': '\033[33m',    # Amarillo
        'ERROR': '\033[31m',      # Rojo
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Agregar color al nivel
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


def setup_logging(app=None, log_file='app.log', log_level='INFO'):
    """
    Configura el sistema de logging de la aplicación
    
    Args:
        app: Instancia de Flask (opcional)
        log_file: Ruta del archivo de log
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    
    # Obtener nivel de logging
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Crear directorio de logs si no existe
    log_dir = os.path.dirname(log_file) if os.path.dirname(log_file) else '.'
    if log_dir != '.' and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Formato para archivos (más detallado)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Formato para consola (más simple y con colores)
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Handler para archivo (con rotación)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(file_formatter)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(console_formatter)
    
    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Limpiar handlers existentes
    root_logger.handlers.clear()
    
    # Agregar nuevos handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Si se proporciona app de Flask, configurar su logger también
    if app:
        app.logger.handlers.clear()
        app.logger.addHandler(file_handler)
        app.logger.addHandler(console_handler)
        app.logger.setLevel(numeric_level)
    
    # Reducir verbosidad de librerías externas
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    return root_logger


def get_logger(name):
    """
    Obtiene un logger configurado
    
    Args:
        name: Nombre del logger (usualmente __name__)
        
    Returns:
        Logger configurado
    """
    return logging.getLogger(name)
